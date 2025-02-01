# Conveyer_belt

The task is to find the speed of the conveyer belt using a .svo file recorded using ZED SDK Camera module. The following are the steps that are used to complete the task.
# Working

**Introduction:** 
This project aims to dynamically determine the speed of a conveyor belt using SVO recordings captured by a ZED Stereo Camera. The camera records the moving belt at 2*720p resolution, with 60 frames per second. Equipped with two or more lenses, each with a separate image sensor, the stereo camera mimics human vision, enabling it to capture 3D images. The project employs both feature extraction and optical flow methods for this task.

**Requirements**
* Python 3.6 or higher
* OpenCV -- pip install opencv-python
* NumPy -- pip install numpy
* pandas -- pip install pandas
* Matplotlib -- pip install matplotlib
* scipy -- pip install scipy

**Installation**
* The device should have atleast 4GB RAM and recommonded is 8GB
* It is mandatory to have NVIDIA GPU recommonded GTX 2060 or higher
* NVIDIA CUDA Toolkit(This will be installed with ZED SDK)
* Download the ZED SDK version 4.x from [StereoLabs website](https://www.stereolabs.com/developers).
* The detail commands to follow are [here](./Descriptions/commands_to_install_ZED_SDK.md)

**Usage**

Run the code using `python main.py [args]`
The arguments give you the flexibility to choose method and window in which you want to run the code.
1) method- Choose between feature selection and optical flow
2) window_size - Choose the window size that is used to smooth the speed values from fluctuation


# Code Structure and functionality

**Initialization of ZED SDK Camera:**
The ZED Camera is initialized using the sl.Camera() object. The video path is set and camera is configured for 
performance depth mode. If Initialization fails a RuntimeError is raised

**Setting Up Variables:**
Then we setup the variables that are future used in the program. Key variables include:
* image_cam, depth_cam for stroing frame and depth data
* prev_depth_map to store previous frame's depthmap
* speed_queue for storing speed values for smoothing
* camera_parameters to sotre intrinsic camera parameters

**Choosing Between Feature Extraction and Optical Flow:**
The method is choosed based on input argument method. 
* Feature extraction, ORB features are detected and matched using FLANN and RANSAC. 
* Optical Flow, Farneback's algorithm is used to compute motion between the frames

Detailed explaination about when to use which method and future developement is discussed [HERE](Descriptions/Choosing_method.md)

**Feature Extraction (ORB Features)**
ORB is fast and effecient for feature detection
* Fast Keypoint Detection: Identifies the keypoints in image by comparing pixel intensities in circulat pattern.
* BRIEF Descriptor: Computes binary descriptors for each keypoint by comparing pixel intensities in a predefined pattern around the keypoint.

The keypoints and descriptos are extracted from a specific Region of Interest, which is cropped from frame using the coordinates provided

**Feature Matching (FLANN with RANSAC)**

Feature matching involves finding similarities between keypoints in two frames. 

* FLANN is used to effieciently match descriptors between frames using approximate nearest neighbours search which has better compuataional effeciency than the brute-force matching
* For each descriptor in first frame, two closest matches are found. It the distance ration between best and second best match is below 0.7(thumb rule but can be choosed differently), the match is considered reliable.
* RANSAC is used to filter out outliers by estimating geometric transformation between matched keypoints. More details about RANSAC and imporovements on filtering are discussed [Here](Descriptions/Outlier_handling.md)


**Optical Flow(Farneback Method)**
* Optical flow is used to estimate the motion of object between two consecutive frames with quick time difference by calculating the displacment vector for each pixel(In this case for every 20 pixels).
* Displacement vector (dx,dy) is retrived from the flow field. Adding the displacement vectors to the current pixels will give the location of the pixel in next frame(2D). Using these 2d coordinateds and depth maps we will find the 3D coordinates of the two pixels and then finds the displacement in 3D.

**Converting Coordinates**

* The coordinates are converted from 2D pixel to 3D world cordinates by using Intrinsic parameters(focal length and principal points)

**Calculating Speed**

* The displacements are calculated using Euclidean distance between the corresponding 3D points.
* The program uses median displacement to avoid ouliers
* The speed is computed as by multiplying the displacment with frames per second

# Handling Noise and outliers

The program uses RANSAC for oulier detection in feature extraction method and in the optical flow module have implicit outlier handling by
Depth Filtering: Removes invalid depth values (negative,zero and non finite)
Median Displacement: Instad of averaging the program uses median displacement to handle outliers
Sampling: Due to sampling the impact of noisy regions is reduced

The program usess moving average to remove the noise in speeds. It uses the window_size(default 5) to minimize the effect of sudden change in the speeds and gives smoother values

**The following plot gives us idea of how using moving average will help to reduce noise caused by fluctuations.** 
![Raw speed vs Moving average speed](Plots/plot.png)

# Output
The output is smoothed speed values recoded at each frame and stored in the results.csv file.

**The following image gives us the distribution of speed values every frame. The plot clearly indicates that the speed of the belt lies between 1.55 m/s to 1.56 m/s**

![Distribution of speeds among frames](Plots/plot_hist_annotated.png)

# Future Developments

* **Deep Learning based Feature Extractors:** We can use learned features from pre-trained models such as D2-Net for better feature extraction and matching

* **Consistency Checks:** Comparing the forward and backward optical flow to remove the inconsistent motion vectors

* **Parallel Processing and Reduced resolution:** Using multi-threading or multiprocessing to handle frame processing can increase the speed of the program. Decreasing the resolution of the frames can also improve the computation speed.

* **Kalman Filter:** We can apply kalman filter to smooth the speeds and reduce noise. Currently moving average is used but Kalman filter can provide significant improvements in terms of accuracy, responsiveness, and adaptability.
