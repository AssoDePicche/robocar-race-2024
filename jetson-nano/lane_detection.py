import cv2
import numpy

def preprocessing_pipeline(frame, blur_kernel_size=3, canny_low_threshold=50, canny_high_threshold=200):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame = cv2.GaussianBlur(frame, (blur_kernel_size, blur_kernel_size), 0)

    frame = cv2.Canny(frame, canny_low_threshold, canny_high_threshold)

    return frame
