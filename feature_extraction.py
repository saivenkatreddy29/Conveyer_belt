import cv2
import numpy as np
import pyzed.sl as sl
from log_values import calculate_speed_3d
from image_projection import get_valid_3d_pairs

def implement_orb(frame, prev_kp, prev_depth_map, curr_depth_map, camera_parameters, prev_des, roi,fps):
    """
    Calculates and returns object speed using ORB features and depth information.

    Args:
        frame (numpy.ndarray): Current video frame
        prev_kp (list): Previous frame keypoints
        prev_depth_map (numpy.ndarray): Depth map of previous frame
        curr_depth_map (numpy.ndarray): Depth map of current frame
        camera_parameters (dict): Camera intrinsic parameters
        prev_des (numpy.ndarray): Previous frame ORB descriptors
        roi (tuple): Region of interest as (x, y, w, h)
        fps (float): frames per second
        

    Returns:
        tuple: Contains:
            - speed (float): Raw calculated speed
            - curr_kp (list): Current frame keypoints
            - curr_des (numpy.ndarray): Current frame descriptors
    """
    curr_kp, curr_des, _ = extract_features(frame, roi)
    matches =  match_features(prev_des, curr_des,prev_kp,curr_kp)
    speed = 0.0  # Default speed if no matches or filtering fails

    if matches:
        src_kp = [prev_kp[m.queryIdx] for m in matches]
        dst_kp = [curr_kp[m.trainIdx] for m in matches]  
        # Get valid 3D point pairs
        src_pts, dst_pts = get_valid_3d_pairs(src_kp, dst_kp, prev_depth_map, curr_depth_map, camera_parameters, (roi[0], roi[1]))
        if src_pts is not None and dst_pts is not None and len(src_pts) > 0:
            speed = calculate_speed_3d(src_pts, dst_pts, fps)
    return speed,curr_kp,curr_des

def extract_features(frame, roi):
    """
    Extract ORB features from a region of interest in a frame.
    Args:
        frame (numpy.ndarray): Input image frame
        roi (tuple): Region of interest as (x, y, w, h)

    Returns:
        tuple: Contains:
            - keypoints (list): Detected ORB keypoints in the ROI
            - descriptors (numpy.ndarray): ORB descriptors for the keypoints
            - roi_frame (n  umpy.ndarray): Cropped region of interest
    """
    x, y, w, h = roi
    roi_frame = frame[y:y+h, x:x+w]
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(roi_frame, None)
    return keypoints, descriptors, roi_frame

# Match features using FLANN
def match_features(des1, des2,kp1,kp2):
    """
    Match ORB features between two frames using FLANN matcher and RANSAC filtering.

    Args:
        des1 (numpy.ndarray): Descriptors from the first frame
        des2 (numpy.ndarray): Descriptors from the second frame
        kp1 (list): Keypoints from the first frame
        kp2 (list): Keypoints from the second frame

    Returns:
        list: Filtered good matches between frames. Each match is a DMatch object 
             containing queryIdx and trainIdx that reference the original keypoints.
             Returns empty list if no good matches are found.

    Notes:
        Uses FLANN (Fast Library for Approximate Nearest Neighbors) with LSH (Locality 
        Sensitive Hashing) for matching. Applies ratio test with threshold 0.7 and 
        RANSAC homography for outlier rejection.
    """

    index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    good_matches = []
    for match_pair in matches:
        if len(match_pair) < 2: # Less than two matches is not reliable
            continue
        m, n = match_pair
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # Use RANSAC to filter outliers
    if len(good_matches) > 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 2)
        _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        good_matches = [m for m, mask_val in zip(good_matches, mask) if mask_val]
    return good_matches
