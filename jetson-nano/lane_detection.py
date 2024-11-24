import cv2
import numpy

def preprocessing_pipeline(frame, blur_kernel_size=3, canny_low_threshold=50, canny_high_threshold=200):
    l, a, b = cv2.split(cv2.cvtColor(frame, cv2.COLOR_BGR2LAB))

    clahe = cv2.createCLAHE(clipLimit=2., tileGridSize=(8, 8))

    l = clahe.apply(l)

    frame = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame = cv2.GaussianBlur(frame, (blur_kernel_size, blur_kernel_size), 0)

    frame = cv2.Canny(frame, canny_low_threshold, canny_high_threshold)

    return frame
