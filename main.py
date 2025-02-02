import os, sys
PATH = os.path.dirname(os.path.abspath(__file__))
# ZED SDK 4.x
import pyzed.sl as sl
sdk_version = sl.Camera().get_sdk_version() 
if sdk_version.split(".")[0] != "4":
    print("This sample is meant to be used with the SDK v4.x, Aborting.")
    exit(1)
import cv2
import numpy as np
import argparse
from collections import deque
from feature_extraction import extract_features, implement_orb
from log_values import log_speed
from optical_flow import implement_optical_flow
from handle_noise import get_smooth_speed



def process_video(log_file_raw,log_file_smooth,window_size=5,fps=60,method = 'optical_flow'):
    """
   Process a ZED camera video file to calculate belt speed using either feature extraction or optical flow methods.

   Args:
       log_file_raw (str): Base path for saving raw speed measurements (method name will be appended)
       log_file_smooth (str): Path for saving smoothed speed measurements
       window_size(int): window_size used to smooth the speed values
       fps (int, optional): Frames per second of the video. Defaults to 60.
       method (str, optional): Speed calculation method - either 'feature_extraction' or 
                             'optical flow'. Defaults to 'optical_flow'.

   Raises:
       RuntimeError: If ZED camera initialization fails

   Notes:
       - Initializes ZED camera in PERFORMANCE depth mode
       - Uses fixed ROI coordinates (512, 250, 190, 150)
       - Processes frames sequentially:
           * Extracts image and depth data
           * Calculates speed using specified method
           * Logs measurements to CSV files
       - Continues until 'q' (key 113) is pressed or end of video
       - Current implementation uses hardcoded ROI instead of detection

   """
    cam = sl.Camera()
    input_type = sl.InputType()
    file_path = os.path.join(PATH, "data", "belt_sample.svo")
    input_type.set_from_svo_file(file_path)
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    if cam.open(init_params) != sl.ERROR_CODE.SUCCESS:
        raise RuntimeError("ZED Camera failed to open.")
    
   # Seting runtime parameters 
    runtime_params = sl.RuntimeParameters()
    image_cam = sl.Mat()
    depth_cam = sl.Mat()
    prev_depth_map = None 
    frame_no = 0
    path_to_speed = log_file_raw+method+'.csv' # add the choosen method
    speed_queue = deque(maxlen=window_size)
    camera_parameters = cam.get_camera_information().camera_configuration.calibration_parameters.left_cam
    
    
    # Initial frame processing
    cam.grab(runtime_params)
    cam.retrieve_image(image_cam, sl.VIEW.LEFT)
    cam.retrieve_measure(depth_cam, sl.MEASURE.DEPTH)
    frame = image_cam.get_data()
    prev_depth_map = depth_cam.get_data().copy()


    roi = (512,250,190,150) # The values are taken from manual identification of ROI
    x, y, w, h = roi
    prev_kp, prev_des, _ = extract_features(frame, roi)
    prev_gray = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
    key = ''

    # The loop will execute unitil the key is quit or the break condition (end of frame) is occured
    while key != 113:
        err = cam.grab(runtime_params)
        if err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            print("End of SVO reached")
            break
        elif err != sl.ERROR_CODE.SUCCESS:
            break

        cam.retrieve_image(image_cam, sl.VIEW.LEFT)
        cam.retrieve_measure(depth_cam, sl.MEASURE.DEPTH)
        frame = image_cam.get_data()
        curr_depth_map = depth_cam.get_data()

        # The block will choose the method based on input 'method'
        if method == 'feature_extraction':
            speed,curr_kp,curr_des = implement_orb(frame,
                                                   prev_kp,
                                                   prev_depth_map,
                                                   curr_depth_map,
                                                   camera_parameters,
                                                   prev_des,
                                                   roi,
                                                   fps)
            prev_kp, prev_des = curr_kp, curr_des
        elif method == 'optical_flow':
            curr_gray = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
            speed = implement_optical_flow(prev_gray,
                                           curr_gray,
                                           prev_depth_map,
                                           curr_depth_map,
                                           camera_parameters,
                                           x,
                                           y,
                                           fps)
            prev_gray = curr_gray

        # Log the speed values and assign the current values to previous values
        log_speed(path_to_speed, frame_no, speed)
        speed_queue.append(speed)
        smooth_speed = get_smooth_speed(speed_queue,window_size)
        log_speed(log_file_smooth,frame_no,smooth_speed)
        prev_depth_map = curr_depth_map.copy()
        frame_no += 1 
    cam.close()


if __name__ == "__main__":
    log_file_raw = "belt_speed_raw_"
    log_file_smooth = "results.csv"
    parser = argparse.ArgumentParser(description="get speed of the conveyor")
    parser.add_argument("--window_size", type=int, default = 5, help="Window size for smoothing.")
    parser.add_argument("--method", type=str, choices=["feature_extraction", "optical_flow"], default="optical_flow", help="Method for processing.")
    args = parser.parse_args()
    try:
        process_video(log_file_raw, log_file_smooth, window_size=args.window_size, fps=60, method=args.method)
    except Exception as e:
        raise Exception("An error occurred while processing the video: " + str(e))

