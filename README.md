# Conveyer_belt

The task is to find the speed of the conveyer belt using a .svo file recorded using ZED SDK Camera module. The following are the steps that are used to complete the task

# Working
There are 4 modules in the [src](./src) directory and main.py is the file that needs to be runned

**Introduction:** 
This project aims to dynamically determine the speed of a conveyor belt using SVO recordings captured by a ZED Stereo Camera. The camera records the moving belt at 2*720p resolution, with 60 frames per second. Equipped with two or more lenses, each with a separate image sensor, the stereo camera mimics human vision, enabling it to capture 3D images. The project employs both feature extraction and optical flow methods for this task.
