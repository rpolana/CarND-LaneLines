# **Finding Lane Lines on the Road** 
[![Udacity - Self-Driving Car NanoDegree](https://s3.amazonaws.com/udacity-sdc/github/shield-carnd.svg)](http://www.udacity.com/drive)

<img src="examples/laneLines_thirdPass.jpg" width="480" alt="Combined Image" />

Overview
---

When we drive, we use our eyes to decide where to go.  The lines on the road that show us where the lanes are act as our constant reference for where to steer the vehicle.  Naturally, one of the first things we would like to do in developing a self-driving car is to automatically detect lane lines using an algorithm.

## Project: **Finding Lane Lines on the Road**
***
In this project, I use the tools we learned about in the lesson to identify lane lines on the road.  I developed a pipeline to find lane lines in an image, testing it on a series of individual images. Later the same pipeline is applied to video streams (processing frames as a series of images), while updating line parameters (slope and mid point of line) using moving averages to smoothen the lane lines in video.

###Algorithm

The pipeline for finding lane lines involves the following steps:

1.Detect edges in image:
 1.Convert image to grayscale
 2.Apply gaussian blur
 3.Use canny edge detector
2.Find one laneline with positive slope and one laneline with negative slope:
 1.Find line segments using Hough transform
 2.For each line segment:
  1.Calculate slope, and x coordinate corresponding to a fixed y coordinate 3/4 down from top  of image
  2.If slope is outside certain thresholds, eliminate corresponding line segment from consideration
  3.Classify line segments into slope positive or slope negative
 3.For positive and negative slopes:
  1.Find average of slopes
  2.Find average of x coordinates corresponding to the fixed y coordinate 3/4 down from top of image
  3.Use the above two (slope and point on line) to extrapolate the line to a single lane line with end points corresponding to two fixed y coordinates: one slightly below center of image and second at bottom of image
 4.Draw the lane lines on original image

The strengths of the algorithm are that because the dominant slope is found after eliminating
lines with slopes outside reasonable thresholds, it appears to be very stable and reliable.
I have also used the image size as part of parameters wherever I believe the parameters are
affected by the image size, so if the image size changes the algorithm is still supposed to
well.

---


###Shortcomings

*Although the algorithm appears to work well even on the challenge video,
the algorithm is very sensitive to the parameters used and there is no guarantee it
will work in untested scenarios.  For example, I have used low thresholds in edge detection to
ensure edges are detected even with low gradients, but there could be lane lines
even outside the range used. Same is true for line detection parameters used for
Hough transform.  Similarly, the lanes are assumed to have slope within certain
range, but these assumptions may not hold true.

*Another shortcoming is: the algorithm will try to find a
lane line even when there is no real lane line, as long as there are some edges
present with slope in the ranges used in the algorithm.


###Possible improvements

*The parameter tuning is done mainly using test images, but it would be better to have a way
to determine algorithm parameters over large set of training images.
*I tried using line segment length or median of slopes to determine the dominant slope, but
my current method of limiting valid slope to a small range and using average within those worked
better than those.

