import numpy as np
import pyzed.sl as sl


# Convert 2D to 3D with camera parameters (unchanged)
def convert_2d_to_3d(x, y, z, camera_params):
    """
    Convert 2D image coordinates and depth to 3D world coordinates using camera parameters.

    Args:
        x (float): x-coordinate in image space in pixels
        y (float): y-coordinate in image space in pixels
        z (float): depth value at the pixel location
        camera_params (object): Camera intrinsic parameters with attributes:
            - fx (float): focal length in x direction
            - fy (float): focal length in y direction
            - cx (float): principal point x-coordinate
            - cy (float): principal point y-coordinate

    Returns:
        tuple: Contains:
            - X (float): x-coordinate in 3D world space
            - Y (float): y-coordinate in 3D world space
            - Z (float): z-coordinate in 3D world space 
    """
    fx = camera_params.fx
    fy = camera_params.fy
    cx = camera_params.cx
    cy = camera_params.cy

    X = (x - cx) * z / fx
    Y = (y - cy) * z / fy
    Z = z

    return X, Y, Z
# Get 3D coordinates from depth map with boundary checks and depth validation
def get_valid_3d_pairs(src_kp, dst_kp, src_depth_map, dst_depth_map, camera_params, roi_offset):

    """
    Extract valid 3D point pairs from matched keypoints using depth information.

   Args:
       src_kp (list): Source keypoints from first frame
       dst_kp (list): Destination keypoints from second frame 
       src_depth_map (numpy.ndarray): Depth map corresponding to first frame
       dst_depth_map (numpy.ndarray): Depth map corresponding to second frame
       camera_params (object): Camera intrinsic parameters for 3D reconstruction
       roi_offset (tuple): (x, y) offset values to translate ROI coordinates to full frame

   Returns:
       tuple: Contains:
           - valid_src_pts (numpy.ndarray): Array of valid 3D points from source frame
           - valid_dst_pts (numpy.ndarray): Array of valid 3D points from destination frame
           Returns (None, None) if no valid pairs are found

   Notes:
       Points are considered invalid if:
       - Depth value is negative or non-finite
       - Point lies outside depth map bounds
       Coordinates are adjusted using roi_offset since keypoints are in ROI space
       but depth maps are in full frame space.
   """
    valid_src_pts = []
    valid_dst_pts = []
    x_offset, y_offset = roi_offset
    
    for skp, dkp in zip(src_kp, dst_kp):
        # Source point
        u_src = int(skp.pt[0] + x_offset)
        v_src = int(skp.pt[1] + y_offset)
        
        # Destination point
        u_dst = int(dkp.pt[0] + x_offset)
        v_dst = int(dkp.pt[1] + y_offset)


        # Get depths for both points
        depth_src = src_depth_map[v_src, u_src]
        depth_dst = dst_depth_map[v_dst, u_dst]
        
        
        # Skip if either depth is invalid
        if depth_src <= 0 or not np.isfinite(depth_src) or depth_dst <= 0 or not np.isfinite(depth_dst):
            continue
            
        # Convert 2D to 3D for both points
        src_3d = convert_2d_to_3d(u_src, v_src, depth_src, camera_params)
        dst_3d = convert_2d_to_3d(u_dst, v_dst, depth_dst, camera_params)
        
        # Append valid pairs
        valid_src_pts.append(src_3d)
        valid_dst_pts.append(dst_3d)

    return np.array(valid_src_pts), np.array(valid_dst_pts)