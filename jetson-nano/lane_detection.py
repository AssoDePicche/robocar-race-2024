import cv2
import numpy

def lane_detection(frame):
    histogram = numpy.sum(frame[frame.shape[0]//2:, :], axis=0)
    midpoint = histogram.shape[0] // 2
    left_base = numpy.argmax(histogram[:midpoint])
    right_base = numpy.argmax(histogram[midpoint:]) + midpoint

    num_windows = 9
    window_height = frame.shape[0] // num_windows
    margin = 100
    minpix = 50

    left_lane_inds = []
    right_lane_inds = []

    left_current = left_base
    right_current = right_base

    nonzero = frame.nonzero()
    nonzero_y = numpy.array(nonzero[0])
    nonzero_x = numpy.array(nonzero[1])

    for window in range(num_windows):
        win_y_low = frame.shape[0] - (window + 1) * window_height
        win_y_high = frame.shape[0] - window * window_height

        left_x_low = left_current - margin
        left_x_high = left_current + margin
        right_x_low = right_current - margin
        right_x_high = right_current + margin

        left_inds = ((nonzero_y >= win_y_low) & (nonzero_y < win_y_high) &
                     (nonzero_x >= left_x_low) & (nonzero_x < left_x_high)).nonzero()[0]
        right_inds = ((nonzero_y >= win_y_low) & (nonzero_y < win_y_high) &
                      (nonzero_x >= right_x_low) & (nonzero_x < right_x_high)).nonzero()[0]

        left_lane_inds.append(left_inds)
        right_lane_inds.append(right_inds)

        if len(left_inds) > minpix:
            left_current = numpy.mean(nonzero_x[left_inds]).astype(int)
        if len(right_inds) > minpix:
            right_current = numpy.mean(nonzero_x[right_inds]).astype(int)

    left_lane_inds = numpy.concatenate(left_lane_inds)
    right_lane_inds = numpy.concatenate(right_lane_inds)

    left_fit = numpy.polyfit(nonzero_y[left_lane_inds], nonzero_x[left_lane_inds], 2)
    right_fit = numpy.polyfit(nonzero_y[right_lane_inds], nonzero_x[right_lane_inds], 2)

    return left_fit, right_fit


def compute_error(frame, left_fit, right_fit):
    height, width = frame.shape

    left_x = numpy.polyval(left_fit, height)

    right_x = numpy.polyval(right_fit, height)

    return (width // 2) - ((left_x + right_x) / 2)


def preprocessing_pipeline(frame, blur_kernel_size=3, canny_low_threshold=50, canny_high_threshold=200):
    l, a, b = cv2.split(cv2.cvtColor(frame, cv2.COLOR_BGR2LAB))

    clahe = cv2.createCLAHE(clipLimit=1., tileGridSize=(4, 4))

    l = clahe.apply(l)

    frame = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame = cv2.GaussianBlur(frame, (blur_kernel_size, blur_kernel_size), 0)

    frame = cv2.threshold(frame, 100, 150, cv2.THRESH_BINARY)[1]

    frame = cv2.Canny(frame, canny_low_threshold, canny_high_threshold)

    return frame
