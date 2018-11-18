# Convert OpenCV k Undistortion Parameters to PTGui a, b, c, d Values

This script shows how to convert k1, k2, k3, k4 undistortion parameters used in OpenCV 
to a, b, c, d parameters used in PTGui.

Test image:

![source.png](source.png)

Test image undistorted by OpenCV using k parameters:

![undistorted_k.png](undistorted_k.png)

Test image undistorted by ImageMagick using a, b, c, d parameters estimated from k:

![undistorted_abcd.png](undistorted_abcd.png)

Difference between undistorted images:

![diff.png](diff.png)
