# RANSAC (RANdom SAmple Consensus):

This method randomly selects a subset of data to fit the model and evaluates the model against the entire dataset and finds the inliers. After the given number of iterations it chooses the best model to fit the inliers.

* It can handle large percentage of outliers and simple to use
* It is computationally extensive to perform iterations to get good model
* The performance is sensitive to number of iterations and inlier threshold

**In future we can use more efficient methods such as Randomized Hough Transform which can find shapes in more noisy environments by accumulating evidence for parameter space and handles outliers.**
