import cv2
import numpy as np
import os


def convert_k_to_abcd(width, height, focal_pixels, k1, k2):
    # Need to approximate a polynomial of power 5 (k3 == 0 and k4 == 0)
    # r'(x) = r(1 + k1 r^2 + k2 r^4)
    # with a polynomial of power 4
    # r''(x) = (a r^3 + b r^2 + c r + d)r
    # To estimate the coefficients of power 4 polynomial five pairs (r'', r) are needed.
    # One pair is fixed: (0, 0). So four more points are chosen evenly between 0 and 1:
    ri = [0.25, 0.5, 0.75, 1.]
    # Goal:
    # sum_i ((r''(r_i) - r'(r_i))^2) -> min
    # This is quadratic form minimization.
    # Take the derivatives with respect to a, b, c, d, set them to zero
    # and solve the linear system.
    
    sumpowri = [np.sum(np.power(ri, i)) for i in range(10)]

    kn2 = k2 * pow((height / 2) / focal_pixels, 4)
    kn1 = k1 * pow((height / 2) / focal_pixels, 2)

    A = [[sumpowri[5], sumpowri[4], sumpowri[3], sumpowri[2]],
         [sumpowri[6], sumpowri[5], sumpowri[4], sumpowri[3]],
         [sumpowri[7], sumpowri[6], sumpowri[5], sumpowri[4]],
         [sumpowri[8], sumpowri[7], sumpowri[6], sumpowri[5]]]

    B = [kn2 * sumpowri[6] + kn1 * sumpowri[4] + sumpowri[2],
         kn2 * sumpowri[7] + kn1 * sumpowri[5] + sumpowri[3],
         kn2 * sumpowri[8] + kn1 * sumpowri[6] + sumpowri[4],
         kn2 * sumpowri[9] + kn1 * sumpowri[7] + sumpowri[5]]

    X = np.linalg.solve(np.array(A), np.array(B))
    a, b, c, d = X[0], X[1], X[2], X[3]    
    return a, b, c, d


def draw_test_grid(width, height):
    step = (int)(width / 32)

    image = 255*np.ones([height, width], np.uint8)

    for i in range(0, width, step):
        image[:,i] = 0
    for i in range(0, height, step):
        image[i,:] = 0

    image[height-1,:] = 0
    image[:,width-1] = 0

    return image
    

def undistort_k(image, focal_pixels, k1, k2, k3, k4):
    fx = fy = focal_pixels
    cx = 0.5 * image.shape[1]
    cy = 0.5 * image.shape[0]
    camMat = np.array([[fx, 0., cx],
                      [0., fy, cy],
                      [0., 0., 1.]])
    distCoefs = np.array([k1, k2, k3, k4])
    undistorted_k = cv2.undistort(image, camMat, distCoefs)
    return undistorted_k


def undistort_abcd(image, a, b, c, d):
    cv2.imwrite('source.png', image)
    cmd = ("convert source.png -distort barrel '%.6f %.6f %.6f %.6f' undistorted_abcd.png" %
        (a, b, c, d))
    os.system(cmd)
    undistorted_abcd = cv2.imread('undistorted_abcd.png', 0)
    return undistorted_abcd
    

def test_convert_k_to_abcd():
    width, height = (2560, 1920)
    focal_pixels = 1242.36
    k1, k2, k3, k4 = (0.03462446, -0.03762977, 0, 0)    
    
    a, b, c, d = convert_k_to_abcd(width, height, focal_pixels, k1, k2)

    print('Image size: %dx%d, focal_pixels: %.6f, k1: %.6f, k2: %.6f' %
         (width, height, focal_pixels, k1, k2))
    print('Estimated a, b, c, d: %.6f, %.6f, %.6f, %.6f' %
         (a, b, c, d))

    image = draw_test_grid(width, height)
    undistorted_k = undistort_k(image, focal_pixels, k1, k2, k3, k4)
    undistorted_abcd = undistort_abcd(image, a, b, c, d)
    
    diff = cv2.absdiff(undistorted_k, undistorted_abcd)

    cv2.imwrite('undistorted_k.png', undistorted_k)
    cv2.imwrite('undistorted_abcd.png', undistorted_abcd)
    cv2.imwrite('diff.png', diff)
    

if __name__ == '__main__':
    test_convert_k_to_abcd()
