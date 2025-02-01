import cv2
import numpy as np
import pyzed.sl as sl
import csv
import os

# Compute real-world speed with valid pairs
def calculate_speed_3d(src_pts, dst_pts, fps):
    """
        Args:
        src_pts (numpy.ndarray): Array of source 3D points
        dst_pts (numpy.ndarray): Array of destination 3D points
        fps (float): Frames per second of the video

    Returns:
        float: Calculated speed in mm/second.
              Returns 0.0 if input points are invalid or speed is below 200 mm/sec.

    Notes:
        - Uses median displacement to reduce impact of outliers
        - Applies threshold of 200 units/second to filter noise
        - Speed = displacement * fps
    """
    if src_pts is None or dst_pts is None or len(src_pts) == 0:
        return 0.0
    displacements = np.linalg.norm(dst_pts - src_pts, axis=1)
    avg_displacement = np.median(displacements)
    speed = avg_displacement * fps
    if speed<200:
        return 0
    return speed

# Log speeds to a file (unchanged)
def log_speed(log_file, frame_no, speed):
    """
    Log frame number and corresponding speed measurements to a CSV file.

    Args:
        log_file (str): Path to the output CSV file
        frame_no (int): Current frame number
        speed (float): Calculated speed value

    Notes:
        - Creates new file with headers if file doesn't exist
        - Appends data if file exists
        - CSV format: Frame,Speed
    """
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Frame', 'Speed'])
        writer.writerow([frame_no, speed])