/* --Sparse Optical Flow Demo Program--
 * Updated based on code written by David Stavens (dstavens@robotics.stanford.edu)
 */

#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace std;
using namespace cv;

int main( int argc, char** argv )
{
    const string filename=argv[1];
    Mat frame;
    
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
    input_video.read(frame);
    
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
    
    namedWindow("movie", WINDOW_AUTOSIZE);
    while(true) {
        input_video >> frame;
        if(!frame.empty()) {
          imshow("movie", frame);
        }

        waitKey(33);
    }
        return 0;
    
}