# coding: utf-8

# # Self-Driving Car Engineer Nanodegree
#
#
# ## Project: **Finding Lane Lines on the Road**
# ***
# In this project, you will use the tools you learned about in the lesson to identify lane lines on the road.  You can develop your pipeline on a series of individual images, and later apply the result to a video stream (really just a series of images). Check out the video clip "raw-lines-example.mp4" (also contained in this repository) to see what the output should look like after using the helper functions below.
#
# Once you have a result that looks roughly like "raw-lines-example.mp4", you'll need to get creative and try to average and/or extrapolate the line segments you've detected to map out the full extent of the lane lines.  You can see an example of the result you're going for in the video "P1_example.mp4".  Ultimately, you would like to draw just one line for the left side of the lane, and one for the right.
#
# In addition to implementing code, there is a brief writeup to complete. The writeup should be completed in a separate file, which can be either a markdown file or a pdf document. There is a [write up template](https://github.com/udacity/CarND-LaneLines-P1/blob/master/writeup_template.md) that can be used to guide the writing process. Completing both the code in the Ipython notebook and the writeup template will cover all of the [rubric points](https://review.udacity.com/#!/rubrics/322/view) for this project.
#
# ---
# Let's have a look at our first image called 'test_images/solidWhiteRight.jpg'.  Run the 2 cells below (hit Shift-Enter or the "play" button above) to display the image.
#
# **Note: If, at any point, you encounter frozen display windows or other confounding issues, you can always start again with a clean slate by going to the "Kernel" menu above and selecting "Restart & Clear Output".**
#
# ---

# **The tools you have are color selection, region of interest selection, grayscaling, Gaussian smoothing, Canny Edge Detection and Hough Tranform line detection.  You  are also free to explore and try other techniques that were not presented in the lesson.  Your goal is piece together a pipeline to detect the line segments in the image, then average/extrapolate them and draw them onto the image for display (as below).  Once you have a working pipeline, try it out on the video stream below.**
#
# ---
#
# <figure>
#  <img src="examples/line-segments-example.jpg" width="380" alt="Combined Image" />
#  <figcaption>
#  <p></p>
#  <p style="text-align: center;"> Your output should look something like this (above) after detecting line segments using the helper functions below </p>
#  </figcaption>
# </figure>
#  <p></p>
# <figure>
#  <img src="examples/laneLines_thirdPass.jpg" width="380" alt="Combined Image" />
#  <figcaption>
#  <p></p>
#  <p style="text-align: center;"> Your goal is to connect/average/extrapolate line segments to get output like this</p>
#  </figcaption>
# </figure>

# **Run the cell below to import some packages.  If you get an `import error` for a package you've already installed, try changing your kernel (select the Kernel menu above --> Change Kernel).  Still have problems?  Try relaunching Jupyter Notebook from the terminal prompt.  Also, consult the forums for more troubleshooting tips.**

# ## Import Packages

# In[1]:


# importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2

# get_ipython().magic(u'matplotlib inline')


# ## Read in an Image

# In[2]:


# reading in an image
image = mpimg.imread('test_images/solidWhiteRight.jpg')

# printing out some stats and plotting
print('This image is:', type(image), 'with dimensions:', image.shape)
# plt.imshow(
#     image)  # if you wanted to show a single color channel image called 'gray', for example, call as plt.imshow(gray, cmap='gray')

# ## Ideas for Lane Detection Pipeline

# **Some OpenCV functions (beyond those introduced in the lesson) that might be useful for this project are:**
#
# `cv2.inRange()` for color selection
# `cv2.fillPoly()` for regions selection
# `cv2.line()` to draw lines on an image given endpoints
# `cv2.addWeighted()` to coadd / overlay two images
# `cv2.cvtColor()` to grayscale or change color
# `cv2.imwrite()` to output images to file
# `cv2.bitwise_and()` to apply a mask to an image
#
# **Check out the OpenCV documentation to learn about these and discover even more awesome functionality!**

# ## Helper Functions

# Below are some helper functions to help get you started. They should look familiar from the lesson!

# In[3]:


import math


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)


def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def region_of_interest(img, vertices):
    """
    Applies an image mask.

    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=5):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).

    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.

    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)


prev_pos_slopes = []
prev_pos_x_mids = []
prev_neg_slopes = []
prev_neg_x_mids = []
prev_size = 15 # keep past slopes and x_mids


def moving_averages(new_slope, new_x_mid, index):
    global prev_pos_slopes, prev_pos_x_mids, prev_neg_slopes, prev_neg_x_mids, prev_size
    if index == 'pos':
        prev_slopes = prev_pos_slopes
        prev_x_mids = prev_pos_x_mids
    else:
        prev_slopes = prev_neg_slopes
        prev_x_mids = prev_neg_x_mids
    prev_slope_sum = np.sum(prev_slopes)
    prev_x_mid_sum = np.sum(prev_x_mids)
    mavg_slope = (prev_slope_sum + new_slope) / (len(prev_slopes) + 1)
    mavg_x_mid = (prev_x_mid_sum + new_x_mid) / (len(prev_x_mids) + 1)
    prev_slopes.append(new_slope)
    prev_x_mids.append(new_x_mid)
    if len(prev_slopes) > prev_size:
        prev_slopes.pop(0)
        prev_x_mids.pop(0)
    return mavg_slope, mavg_x_mid


def clear_moving_averages():
    global prev_pos_slopes, prev_pos_x_mids, prev_neg_slopes, prev_neg_x_mids, prev_size
    prev_pos_slopes = []
    prev_pos_x_mids = []
    prev_neg_slopes = []
    prev_neg_x_mids = []


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                            maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    lines_new = []
    pos_slopes = []
    pos_intercepts = []
    pos_sq_distances = np.zeros([len(lines)])
    neg_slopes = []
    neg_intercepts = []
    neg_sq_distances = np.zeros([len(lines)])
    pos_len = 0
    neg_len = 0
    y_mid = img.shape[0] * 3/4
    min_pos_slope = 0.5
    max_pos_slope = 0.8
    min_neg_slope = -0.8
    max_neg_slope = -0.5
    min_abs_slope = 0.01  # to ignore almost vertical lines
    pos_x_mids = []
    neg_x_mids = []
    if not lines is None: # sometime no lines are detected and lines becomes None
        # eliminate lines that are outside slope limits specified
        # calculate intercepts at y_mid within roi: at 3/4 down from top of image
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x2 != x1:
                    slope = (y2-y1)/(x2-x1)
                    if math.fabs(slope) < min_abs_slope:
                        continue   # ignore almost vertical lines
                    intercept = y2 - slope * x2
                    x_mid = (y_mid - intercept) / slope
                    sq_distance = (y2 - y1) * (y2 - y1) + (x2 - x1) * (x2 - x1)
                    # print("line: slope={:.2f}, x_mid={:.2f}, intercept={:.2f}:({:.2f},{:.2f})-({:.2f},{:.2f})".format(
                    #         slope, x_mid, intercept, x1, y1, x2, y2))
                    if (slope >= min_pos_slope) and (slope <= max_pos_slope):
                        pos_slopes.append(slope)
                        pos_intercepts.append(intercept)
                        pos_sq_distances[pos_len] = sq_distance
                        pos_x_mids.append(x_mid)
                        pos_len += 1
                        # print('Appended slope = {:.2f}'.format(slope))
                    elif (slope <= max_neg_slope) and (slope >= min_neg_slope):
                        neg_slopes.append(slope)
                        neg_intercepts.append(intercept)
                        neg_sq_distances[neg_len] = sq_distance
                        neg_x_mids.append(x_mid)
                        neg_len += 1
                        # print('Appended slope = {:.2f}'.format(slope))
                    else:
                        # print('Excluded line with slope = {:.2f}'.format(slope))
                        pass

        # print('Pos slopes:', pos_slopes)
        # print('Pos x_mids:', pos_x_mids)
        # print('Pos intercepts:', pos_intercepts)
        # print('Neg slopes:', neg_slopes)
        # print('Neg x_mids:', neg_x_mids)
        # print('Neg intercepts:', neg_intercepts)
        pos_len = len(pos_slopes)
        y1 = img.shape[0] - 1
        y2 = int(img.shape[0]*5/8)
        if pos_len > 0:
            # # # pos_median_index = np.argsort(pos_slopes)[len(pos_slopes) // 2]
            # # pos_mid1 = pos_slopes.index(np.percentile(pos_slopes, 25, interpolation='nearest'))
            # # pos_mid2 = pos_slopes.index(np.percentile(pos_slopes, 75, interpolation='nearest'))
            # pos_sq_distance_max_index = pos_sq_distances.argmax()
            # # # pos_slope = pos_slopes[neg_median_index]
            # # pos_slope = np.average(pos_slopes[pos_mid1:pos_mid2+1])
            # pos_slope = pos_slopes[pos_sq_distance_max_index]
            # # # pos_intercept = pos_intercepts[pos_median_index]
            # # pos_intercept = np.average(pos_intercepts[pos_mid1:pos_mid2+1])
            # pos_intercept = pos_intercepts[pos_sq_distance_max_index]
            pos_slope = np.average(pos_slopes)
            pos_x_mid = np.average(pos_x_mids)
            # pos_intercept = np.average(pos_intercepts)
            pos_slope, pos_x_mid = moving_averages(pos_slope, pos_x_mid, 'pos')
            pos_intercept = y_mid - pos_slope * pos_x_mid
            x1 = int((y1 - pos_intercept)/pos_slope)
            x2 = int((y2 - pos_intercept)/pos_slope)
            lines_new.append([[x1, y1, x2, y2]])
            # print("pos laneline: slope={:.2f}, x_mid={:.2f}, intercept={:.2f}:({:.2f},{:.2f})-({:.2f},{:.2f})".format(
            #     pos_slope, pos_x_mid, pos_intercept, x1,y1,x2,y2))
        neg_len = len(neg_slopes)
        if neg_len > 0:
            # # # neg_median_index = np.argsort(neg_slopes)[len(neg_slopes) // 2]
            # # neg_mid1 = neg_slopes.index(np.percentile(neg_slopes, 25, interpolation='nearest'))
            # # neg_mid2 = neg_slopes.index(np.percentile(neg_slopes, 75, interpolation='nearest'))
            # neg_sq_distance_max_index = neg_sq_distances.argmax()
            # # # neg_slope = neg_slopes[neg_median_index]
            # # neg_slope = np.average(neg_slopes[neg_mid1:neg_mid2+1])
            # neg_slope = neg_slopes[neg_sq_distance_max_index]
            # # # neg_intercept = neg_intercepts[neg_median_index]
            # # neg_intercept = np.average(neg_slopes[neg_mid1:neg_mid2+1])
            # neg_intercept = neg_intercepts[neg_sq_distance_max_index]
            neg_slope = np.average(neg_slopes)
            neg_x_mid = np.average(neg_x_mids)
            neg_slope, neg_x_mid = moving_averages(neg_slope, neg_x_mid, 'neg')
            # neg_intercept = np.average(neg_intercepts)
            neg_intercept = y_mid - neg_slope * neg_x_mid
            x1 = int((y1 - neg_intercept)/neg_slope)
            x2 = int((y2 - neg_intercept)/neg_slope)
            lines_new.append([[x1, y1, x2, y2]])
            # print("neg laneline: slope={:.2f}, x_mid={:.2f}, intercept={:.2f}:({:.2f},{:.2f})-({:.2f},{:.2f})".format(
            #     neg_slope, neg_x_mid, neg_intercept, x1,y1,x2,y2))


        draw_lines(line_img, lines_new)
        # cv2.imshow('before_lines', img)
        # temp = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        # draw_lines(temp, lines)
        # cv2.imshow('lines_original', temp)
        # temp2 = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        # draw_lines(temp2, lines_new)
        # cv2.imshow('lane_lines', temp2)
        # cv2.waitKey(1000)
    return line_img


# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, α=0.8, β=1., γ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.

    `initial_img` should be the image before any processing.

    The result image is computed as follows:

    initial_img * α + img * β + γ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, γ)


# ## Test Images
#
# Build your pipeline to work on the images in the directory "test_images"
# **You should make sure your pipeline works well on these images before you try the videos.**

# In[4]:


import os

os.listdir("test_images/")


# ## Build a Lane Finding Pipeline
#
#

# Build the pipeline and run your solution on all test_images. Make copies into the `test_images_output` directory, and you can use the images in your writeup report.
#
# Try tuning the various parameters, especially the low and high Canny thresholds as well as the Hough lines parameters.

# In[8]:


# TODO: Build your pipeline that will draw lane lines on the test_images
# then save them to the test_images_output directory.
def lane_finding_pipeline(image):
    # get gray scale first since all processing steps are on grayscale only
    gray = grayscale(image)
    # Define a kernel size and apply Gaussian smoothing
    kernel_size = 5
    blur_gray = gaussian_blur(gray, kernel_size)
    # Define our parameters for Canny and apply
    low_threshold = 60
    high_threshold = 120
    edges = canny(blur_gray, low_threshold, high_threshold)
    # cv2.imshow('edges', edges)
    # cv2.waitKey(1000)
    # Next we'll create a masked edges image using cv2.fillPoly()
    mask = np.zeros_like(edges)
    ignore_mask_color = 255
    # This time we are defining a four sided polygon to mask
    imshape = image.shape
    vertices = np.array([[(int(imshape[1]*1/16), int(imshape[0])),
                          (int(imshape[1] * 7 / 16), int(imshape[0] * 5 / 8)),
                          (int(imshape[1] * 9 / 16), int(imshape[0] * 5 / 8)),
                          (int(imshape[1]*15/16), int(imshape[0]))]],
                        dtype=np.int32)
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    # cv2.imshow('mask', mask)
    # cv2.waitKey(1000)
    masked_edges = cv2.bitwise_and(edges, mask)
    # cv2.imshow('masked_edges', masked_edges)
    # cv2.waitKey(1000)
    # Define the Hough transform parameters
    # Make a blank the same size as our image to draw on
    rho = 2
    theta = np.pi / 180
    threshold = 50
    min_line_length = 25
    max_line_gap = 100
    # Run Hough on edge detected image
    line_image = hough_lines(masked_edges, rho, theta, threshold,
                             min_line_length, max_line_gap)
    # cv2.imshow('line_image', line_image)
    # cv2.waitKey(1000)
    # # Create a "color" binary image to combine with line image
    # color_edges = np.dstack((masked_edges, masked_edges, masked_edges))
    # cv2.imshow('color_edges', color_edges)
    # cv2.waitKey(1000)
    # Draw the lines on the edge image
    combo = weighted_img(line_image, image, 0.8, 1, 0)
    # cv2.imshow('combo', combo)
    # cv2.waitKey(1000)
    return combo

IMAGE_DIR = "test_images/"
for imagefile in os.listdir(IMAGE_DIR):
    if imagefile.split('.')[-1] == 'jpg':
        image = cv2.imread(os.path.join(IMAGE_DIR, imagefile))
        cv2.imshow('image', image)
        result = lane_finding_pipeline(image)
        cv2.imshow('result', result)
        cv2.waitKey(3000)
        clear_moving_averages()


# ## Test on Videos
#
# You know what's cooler than drawing lanes over images? Drawing lanes over video!
#
# We can test our solution on two provided videos:
#
# `solidWhiteRight.mp4`
#
# `solidYellowLeft.mp4`
#
# **Note: if you get an import error when you run the next cell, try changing your kernel (select the Kernel menu above --> Change Kernel). Still have problems? Try relaunching Jupyter Notebook from the terminal prompt. Also, consult the forums for more troubleshooting tips.**
#
# **If you get an error that looks like this:**
# ```
# NeedDownloadError: Need ffmpeg exe.
# You can download it by calling:
# imageio.plugins.ffmpeg.download()
# ```
# **Follow the instructions in the error message and check out [this forum post](https://discussions.udacity.com/t/project-error-of-test-on-videos/274082) for more troubleshooting tips across operating systems.**

# In[ ]:


# Import everything needed to edit/save/watch video clips
from moviepy.editor import VideoFileClip
from IPython.display import HTML


# In[ ]:


def process_image(image):
    # NOTE: The output you return should be a color image (3 channel) for processing video below
    # TODO: put your pipeline here,
    # you should return the final output (image where lines are drawn on lanes)
    result = lane_finding_pipeline(image)
    return result


# Let's try the one with the solid white lane on the right first ...

# In[ ]:


white_output = 'test_videos_output/solidWhiteRight.mp4'
## To speed up the testing process you may want to try your pipeline on a shorter subclip of the video
## To do so add .subclip(start_second,end_second) to the end of the line below
## Where start_second and end_second are integer values representing the start and end of the subclip
## You may also uncomment the following line for a subclip of the first 5 seconds
##clip1 = VideoFileClip("test_videos/solidWhiteRight.mp4").subclip(0,5)
clip1 = VideoFileClip("test_videos/solidWhiteRight.mp4")
white_clip = clip1.fl_image(process_image)  # NOTE: this function expects color images!!
clear_moving_averages()

class timeit():
    from datetime import datetime

    def __enter__(self):
        self.tic = self.datetime.now()

    def __exit__(self, *args, **kwargs):
        print('runtime: {}'.format(self.datetime.now() - self.tic))


# get_ipython().magic(u'time white_clip.write_videofile(white_output, audio=False)')

with timeit():
    white_clip.write_videofile(white_output, audio=False)

# Play the video inline, or if you prefer find the video in your filesystem (should be in the same directory) and play it in your video player of choice.

# In[ ]:


HTML("""
<video width="960" height="540" controls>
  <source src="{0}">
</video>
""".format(white_output))

# ## Improve the draw_lines() function
#
# **At this point, if you were successful with making the pipeline and tuning parameters, you probably have the Hough line segments drawn onto the road, but what about identifying the full extent of the lane and marking it clearly as in the example video (P1_example.mp4)?  Think about defining a line to run the full length of the visible lane based on the line segments you identified with the Hough Transform. As mentioned previously, try to average and/or extrapolate the line segments you've detected to map out the full extent of the lane lines. You can see an example of the result you're going for in the video "P1_example.mp4".**
#
# **Go back and modify your draw_lines function accordingly and try re-running your pipeline. The new output should draw a single, solid line over the left lane line and a single, solid line over the right lane line. The lines should start from the bottom of the image and extend out to the top of the region of interest.**

# Now for the one with the solid yellow lane on the left. This one's more tricky!

# In[ ]:


yellow_output = 'test_videos_output/solidYellowLeft.mp4'
## To speed up the testing process you may want to try your pipeline on a shorter subclip of the video
## To do so add .subclip(start_second,end_second) to the end of the line below
## Where start_second and end_second are integer values representing the start and end of the subclip
## You may also uncomment the following line for a subclip of the first 5 seconds
##clip2 = VideoFileClip('test_videos/solidYellowLeft.mp4').subclip(0,5)
clip2 = VideoFileClip('test_videos/solidYellowLeft.mp4')
yellow_clip = clip2.fl_image(process_image)
clear_moving_averages()

# get_ipython().magic(u'time yellow_clip.write_videofile(yellow_output, audio=False)')
with timeit():
    yellow_clip.write_videofile(yellow_output, audio=False)

# In[ ]:


HTML("""
<video width="960" height="540" controls>
  <source src="{0}">
</video>
""".format(yellow_output))

# ## Writeup and Submission
#
# If you're satisfied with your video outputs, it's time to make the report writeup in a pdf or markdown file. Once you have this Ipython notebook ready along with the writeup, it's time to submit for review! Here is a [link](https://github.com/udacity/CarND-LaneLines-P1/blob/master/writeup_template.md) to the writeup template file.
#

# ## Optional Challenge
#
# Try your lane finding pipeline on the video below.  Does it still work?  Can you figure out a way to make it more robust?  If you're up for the challenge, modify your pipeline so it works with this video and submit it along with the rest of your project!

# In[ ]:


challenge_output = 'test_videos_output/challenge.mp4'
## To speed up the testing process you may want to try your pipeline on a shorter subclip of the video
## To do so add .subclip(start_second,end_second) to the end of the line below
## Where start_second and end_second are integer values representing the start and end of the subclip
## You may also uncomment the following line for a subclip of the first 5 seconds
##clip3 = VideoFileClip('test_videos/challenge.mp4').subclip(0,5)
clip3 = VideoFileClip('test_videos/challenge.mp4')
challenge_clip = clip3.fl_image(process_image)
clear_moving_averages()

# get_ipython().magic(u'time challenge_clip.write_videofile(challenge_output, audio=False)')
with timeit():
    challenge_clip.write_videofile(challenge_output, audio=False)

# In[ ]:


HTML("""
<video width="960" height="540" controls>
  <source src="{0}">
</video>
""".format(challenge_output))
