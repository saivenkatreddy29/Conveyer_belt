# Choosing the method to obtain the speed dynamically
I have implemented two methods to calculate the speed

**ORB Features with FLANN Matcher and RANSAC Filtering:**
* This method is good when there are easily identifiable features in the frame.
* This method is robust against noise and occlusions.
* The performance might reduce with large scale changes in scene

**Farneback Optical Flow:**

* This method is good when the motion is smooth and continuous, provides dense flow of vectors representing movement across the entire frame(I used a pixel for every 20 pixels for computational efficiency)
* Used in real time as it is less dependent on features
* Struggles with rapid movements or when there is significant motion blur

**More robust techniques such as CNN's can be used for robust feature extraction in future**
	
