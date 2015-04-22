/* --Sparse Optical Flow Demo Program--
 * Updated based on code written by David Stavens (dstavens@robotics.stanford.edu)
 * http://robots.stanford.edu/cs223b05/notes/CS%20223-B%20T1%20stavens_opencv_optical_flow.pdf
 */

#include <cstdio>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

#define CAP_PROP_FRAME_HEIGHT CV_CAP_PROP_FRAME_HEIGHT
#define CAP_PROP_FRAME_WIDTH CV_CAP_PROP_FRAME_WIDTH
#define CAP_PROP_POS_AVI_RATIO CV_CAP_PROP_POS_AVI_RATIO
#define CAP_PROP_POS_FRAMES CV_CAP_PROP_POS_FRAMES
#define CAP_PROP_POS_FRAMES CV_CAP_PROP_POS_FRAMES
#define CAP_PROP_POS_FRAMES CV_CAP_PROP_POS_FRAMES

using namespace std;
using namespace cv;

static const double pi = 3.14159265358979323846;

inline static double square(int a)
{
    return a * a;
}

/* This is just an inline that allocates images. I did this to reduce clutter in the
 * actual computer vision algorithmic code. Basically it allocates the requested image
 * unless that image is already non-NULL. It always leaves a non-NULL image as-is even
 * if that image's size, depth, and/or channels are different than the request.
 */
inline static void allocateOnDemand( Mat **img, Size size, int depth, int channels)
{
    if ( *img != NULL ) return;
    //*img=create( size, depth, channels );
    if ( *img == NULL )
    {
        fprintf(stderr, "Error: Couldn't allocate image. Out of memory?\n");
        exit(-1);
    }
}

int main( int argc, char** argv )
{
    const string filename=argv[1];
    Mat frameForProperties;
    
    //Open the input video
    //changed CvCapture to VideoCapture
    VideoCapture input_video(filename);
    
    //Check to make sure video exists and is in a OpenCV compatible format
    if(!input_video.isOpened()) {
        cout << "Cannot open file. Check path and format" << endl;
        return -1;
    }
    //old hack to get video properties, not sure if still needed
    //changed cvQueryFrame to input_video.read
    input_video.read(frameForProperties);
    
    /* Read the video's frame size out of the AVI. */
    //changed CvSize to Size, changed cvGetCaptureProperty to input_video.get
    Size frame_size;
    frame_size.height=(int)input_video.get(CAP_PROP_FRAME_HEIGHT);
    frame_size.width =(int)input_video.get(CAP_PROP_FRAME_WIDTH );
    
    /* Determine the number of frames in the AVI. */
    long number_of_frames;
    
    /* Go to the end of the AVI (ie: the fraction is "1") */
    //changed cvSetCaptureProperty to input_video.set
    input_video.set(CAP_PROP_POS_AVI_RATIO, 1. );
    
    /* Now that we're at the end, read the AVI position in frames */
    //changed cvCaptureProperty to input_video.get
    number_of_frames = (int) input_video.get(CAP_PROP_POS_FRAMES );
    
    /* Return to the beginning */
    //changed cvSetCaptureProperty to input_video.set
    input_video.set(CAP_PROP_POS_FRAMES, 0. );
    
    
    //Set up windows to display output
    //changed cvNamedWindow to namedWindow
    namedWindow("Optical Flow", WINDOW_AUTOSIZE);
    long current_frame=0;
    
    while(true) {
        //changed IplImage to Mat
        static Mat *frame = NULL, *frame1 = NULL, *frame1_1C = NULL, *frame2_1C =
        NULL, *eig_image = NULL, *temp_image = NULL, *pyramid1 = NULL, *pyramid2 = NULL;
        
        /* Go to the frame we want. Important if multiple frames are queried in
         * the loop which they of course are for optical flow. Note that the very
         * first call to this is actually not needed. (Because the correct position
         * is set outsite the for() loop.)
         */
        //changed cvSetCapture Property to input_video.set
        input_video.set(CAP_PROP_POS_FRAMES, current_frame );
        
        /* Get the next frame of the video.*/
        //changed cvQueryFrame to input_video >> *frame
        input_video >> *frame;
        if (frame == NULL) {
            /* Why did we get a NULL frame? We shouldn't be at the end. */
            cout << "Error: Hmm. The end came sooner than we thought" << endl;
            return -1;
        }
        /* Allocate another image if not already allocated.
         * Image has ONE challenge of color (ie: monochrome) with 8-bit "color" depth.
         * This is the image format OpenCV algorithms actually operate on (mostly).
         */
        //probably take out allocate on demand in favor of making a Mat image with constructor
        //allocateOnDemand( &frame1_1C, frame_size, CV_8U, 1 );
        frame1_1C->create(frame_size, CV_8U);
        /* Convert whatever the AVI image format is into OpenCV's preferred format.
         * AND flip the image vertically. Flip is a shameless hack. OpenCV reads
         * in AVIs upside-down by default. (No comment :-))
         */
        
        //change cvConvertImage to flip
        cv::flip(*frame, *frame1_1C, 0);
        
        /* We'll make a full color backup of this frame so that we can draw on it.
         * (It's not the best idea to draw on the static memory space of cvQueryFrame().)
         */
        frame1->create(frame_size, CV_8U);
        cv::flip(*frame, *frame1, 0);
        
        /* Get the second frame of video. Sample principles as the first. */
        //changed cvQueryFrame to input_video >> *frame, followed frame1_1C procedure
        input_video >> *frame;
        if (frame == NULL) {
            fprintf(stderr, "Error: Hmm. The end came sooner than we thought.\n");
            return -1;
        }
        frame2_1C->create(frame_size, CV_8U );
        cv::flip(*frame, *frame2_1C, 0);
        
        /* Shi and Tomasi Feature Tracking! */
        /* Preparation: Allocate the necessary storage. */
        //change allocateOnDemand to ->create
        eig_image->create(frame_size, CV_32F);
        temp_image->create( frame_size, CV_32F);
        
        /* Preparation: This array will contain the features found in frame 1. */
        Point frame1_features[400];
        
        /* Preparation: BEFORE the function call this variable is the array size
         * (or the maximum number of features to find). AFTER the function call
         * this variable is the number of features actually found.
         */
        int number_of_features;
        
        /* I'm hardcoding this at 400. But you should make this a #define so that you can
         * change the number of features you use for an accuracy/speed tradeoff analysis.
         */
        number_of_features = 400;
        
        /* Actually run the Shi and Tomasi algorithm!!
         * "frame1_1C" is the input image.
         * "eig_image" and "temp_image" are just workspace for the algorithm.
         * The first ".01" specifies the minimum quality of the features (based on the
         eigenvalues).
         * The second ".01" specifies the minimum Euclidean distance between features.
         * "NULL" means use the entire input image. You could point to a part of the
         image.
         * WHEN THE ALGORITHM RETURNS:
         * "frame1_features" will contain the feature points.
         * "number_of_features" will be set to a value <= 400 indicating the number of
         feature points found.
         */
        cv::goodFeaturesToTrack(*frame1_1C, frame1_features, number_of_features, .01, .01);
        /* Pyramidal Lucas Kanade Optical Flow! */
        /* This array will contain the locations of the points from frame 1 in frame 2. */
        Point frame2_features[400];
        
        /* The i-th element of this array will be non-zero if and only if the i-th feature
         of
         * frame 1 was found in frame 2.
         */
        char optical_flow_found_feature[400];
        
        /* The i-th element of this array is the error in the optical flow for the i-th
         feature
         * of frame1 as found in frame 2. If the i-th feature was not found (see the
         array above)
         * I think the i-th entry in this array is undefined.
         */
        float optical_flow_feature_error[400];
        
        /* This is the window size to use to avoid the aperture problem (see slide
         "Optical Flow: Overview"). */
        Size optical_flow_window = Size(3,3);
        
        /* This termination criteria tells the algorithm to stop when it has either done
         20 iterations or when
         * epsilon is better than .3. You can play with these parameters for speed vs.
         accuracy but these values
         * work pretty well in many situations.
         */
        TermCriteria optical_flow_termination_criteria = TermCriteria( TermCriteria::COUNT + TermCriteria::EPS, 20, .3 );
        
        /* This is some workspace for the algorithm.
         * (The algorithm actually carves the image into pyramids of different resolutions
         .)
         */
        pyramid1->create(frame_size, CV_8U);
        pyramid2->create( frame_size, CV_8U);
        /* Actually run Pyramidal Lucas Kanade Optical Flow!!
         * "frame1_1C" is the first frame with the known features.
         * "frame2_1C" is the second frame where we want to find the first frame's
         features.
         * "pyramid1" and "pyramid2" are workspace for the algorithm.
         * "frame1_features" are the features from the first frame.
         * "frame2_features" is the (outputted) locations of those features in the second
         frame.
         * "number_of_features" is the number of features in the frame1_features array.
         * "optical_flow_window" is the size of the window to use to avoid the aperture
         problem.
         * "5" is the maximum number of pyramids to use. 0 would be just one level.
         * "optical_flow_found_feature" is as described above (non-zero iff feature found
         by the flow).
         * "optical_flow_feature_error" is as described above (error in the flow for this
         feature).
         * "optical_flow_termination_criteria" is as described above (how long the
         algorithm should look).
         * "0" means disable enhancements. (For example, the second aray isn't preinitialized
         with guesses.)
         */
        cv::calcOpticalFlowPyrLK(*frame1_1C, *frame2_1C, frame1_features, frame2_features,
                                 number_of_features, optical_flow_window, 5,
                                 optical_flow_found_feature, optical_flow_feature_error,
                                 optical_flow_termination_criteria, 0 );
        
        /* For fun (and debugging :)), let's draw the flow field. */
        for(int i = 0; i < number_of_features; i++)
        {
            /* If Pyramidal Lucas Kanade didn't really find the feature, skip it. */
            if ( optical_flow_found_feature[i] == 0 ) continue;
            int line_thickness; line_thickness = 1;
            /* CV_RGB(red, green, blue) is the red, green, and blue components
             * of the color you want, each out of 255.
             */
            Scalar line_color;
            line_color=Scalar(255,0,0);
            /* Let's make the flow field look nice with arrows. */
            /* The arrows will be a bit too short for a nice visualization because of the
             high framerate
             * (ie: there's not much motion between the frames). So let's lengthen them
             by a factor of 3.
             */
            Point p,q;
            p.x = (int) frame1_features[i].x;
            p.y = (int) frame1_features[i].y;
            q.x = (int) frame2_features[i].x;
            q.y = (int) frame2_features[i].y;
            double angle; angle = atan2( (double) p.y - q.y, (double) p.x - q.x );
            double hypotenuse; hypotenuse = sqrt( square(p.y - q.y) + square(p.x - q.x) )
            ;
            /* Here we lengthen the arrow by a factor of three. */
            q.x = (int) (p.x - 3 * hypotenuse * cos(angle));
            q.y = (int) (p.y - 3 * hypotenuse * sin(angle));
            /* Now we draw the main line of the arrow. */
            /* "frame1" is the frame to draw on.
             * "p" is the point where the line begins.
             * "q" is the point where the line stops.
             * "CV_AA" means antialiased drawing.
             * "0" means no fractional bits in the center cooridinate or radius.
             */
            
            cv::line( *frame1, p, q, line_color, line_thickness, LINE_AA, 0 );
            /* Now draw the tips of the arrow. I do some scaling so that the
             * tips look proportional to the main line of the arrow.
             */
            p.x = (int) (q.x + 9 * cos(angle + pi / 4));
            p.y = (int) (q.y + 9 * sin(angle + pi / 4));
            cv::line( *frame1, p, q, line_color, line_thickness, LINE_AA, 0 );
            p.x = (int) (q.x + 9 * cos(angle - pi / 4));
            p.y = (int) (q.y + 9 * sin(angle - pi / 4));
            cv::line( *frame1, p, q, line_color, line_thickness, LINE_AA, 0 );
        }
        /* Now display the image we drew on. Recall that "Optical Flow" is the name of
         * the window we created above.
         */
         imshow("Optical Flow", *frame1);
        /* And wait for the user to press a key (so the user has time to look at the
         image).
         * If the argument is 0 then it waits forever otherwise it waits that number of
         milliseconds.
         * The return value is the key the user pressed.
         */
        int key_pressed;
        key_pressed = waitKey(0);
        /* If the users pushes "b" or "B" go back one frame.
         * Otherwise go forward one frame.
         */
        if (key_pressed == 'b' || key_pressed == 'B') current_frame--;
        else current_frame++;
        /* Don't run past the front/end of the AVI. */
        if (current_frame < 0) current_frame = 0;
        if (current_frame >= number_of_frames - 1) current_frame = number_of_frames - 2;
    }
    return 0;
}