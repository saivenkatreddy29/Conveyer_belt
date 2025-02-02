import cv2
import numpy as np
import pandas as pd


def get_smooth_speed(speeds_queue,window_size):
    """
   Calculate smoothed speed using moving average over a window of speed measurements.

   Args:
       speeds_queue (list): Queue containing historical speed measurements
       window_size (int): Number of measurements to use for smoothing

   Returns:
       float: Smoothed speed value. 
             Returns current speed if queue length is less than window size,
             otherwise returns mean of last window_size measurements.

   Notes:
       - Uses simple moving average for smoothing
      
   """
    if len(speeds_queue)<window_size:
        return speeds_queue[-1]
    return np.mean(speeds_queue)