/* --Sparse Optical Flow Demo Program--
 * Updated based on code written by David Stavens (dstavens@robotics.stanford.edu)
 */

#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace std;
using namespace cv;

/* This is just an inline that allocates images. I did this to reduce clutter in the
 * actual computer vision algorithmic code. Basically it allocates the requested image
 * unless that image is already non-NULL. It always leaves a non-NULL image as-is even
 * if that image's size, depth, and/or channels are different than the request.
 */
inline static void allocateOnDemand( Mat **img, Size size, int depth, int channels)
{
    if ( *img != NULL ) return;
   // *img.create( size, depth, channels );
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
        allocateOnDemand( &frame1_1C, frame_size, CV_8U, 1 );
    
    }
        return 0;
    
}