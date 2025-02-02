
from scipy.ndimage import map_coordinates
import cv2
import numpy as np
import pyzed.sl as sl
from image_projection import convert_2d_to_3d
from log_values import calculate_speed_3d

def implement_optical_flow(prev_gray,curr_gray,prev_depth_map,curr_depth_map,camera_parameters,x,y,fps):

    """
   Calculate object speed using Farneback optical flow and depth information.

   Args:
       prev_gray (numpy.ndarray): Previous frame in grayscale
       curr_gray (numpy.ndarray): Current frame in grayscale
       prev_depth_map (numpy.ndarray): Depth map corresponding to previous frame
       curr_depth_map (numpy.ndarray): Depth map corresponding to current frame
       camera_parameters (object): Camera intrinsic parameters for 3D reconstruction
       x (int): X-coordinate offset of the ROI
       y (int): Y-coordinate offset of the ROI
       fps (float): frames per second

   Returns:
       float: Calculated speed between frames based on optical flow and 3D reconstruction.
              Returns 0.0 if no valid flow points are found.

   Notes:
       - Uses Farneback optical flow with fixed parameters for dense flow calculation
       - Samples flow points every 20 pixels in both directions
       - Interpolates depth values for sub-pixel flow locations
       - Filters out negative and non finite depth values
       - Converts 2D flow to 3D motion using depth information
   """

    flow = cv2.calcOpticalFlowFarneback(
    prev_gray, curr_gray, None,
    pyr_scale=0.5, levels=3, winsize=15, iterations=3,
    poly_n=5, poly_sigma=1.2, flags=0)

    src_pts = []
    dst_pts = []
    for i in range(0, flow.shape[0], 20):
        for j in range(0, flow.shape[1], 20):
            dx, dy = flow[i, j]
            u_prev = x + j
            v_prev = y + i
            u_curr = u_prev + dx
            v_curr = v_prev + dy

            # Get previous depth
            if 0 <= u_prev < prev_depth_map.shape[1] and 0 <= v_prev < prev_depth_map.shape[0]:
                depth_prev = prev_depth_map[v_prev, u_prev]
            else:
                continue

            # Get current depth with interpolation
            try:
                depth_curr = map_coordinates(
                    curr_depth_map,
                    [[v_curr], [u_curr]],
                    order=1, mode='nearest'
                )[0]
            except:
                continue

            if depth_prev <= 0 or depth_curr <= 0 or not np.isfinite(depth_prev) or not np.isfinite(depth_curr):
                continue

            # Convert to 3D
            X_prev, Y_prev, Z_prev = convert_2d_to_3d(u_prev, v_prev, depth_prev, camera_parameters)
            X_curr, Y_curr, Z_curr = convert_2d_to_3d(u_curr, v_curr, depth_curr, camera_parameters)
            src_pts.append((X_prev,Y_prev,Z_prev))
            dst_pts.append((X_curr,Y_curr,Z_curr))
    speed = calculate_speed_3d(np.array(src_pts), np.array(dst_pts), fps)
    return speed