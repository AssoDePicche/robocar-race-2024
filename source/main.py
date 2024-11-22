import cv2
import numpy
import serial


class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp

        self.ki = ki

        self.kd = kd

        self.previous_error = 0.0

        self.integral = 0.0

    def compute(self, error):
        self.integral += error

        derivative = error - self.previous_error

        self.previous_error = error

        return self.kp * error + self.ki * self.integral + self.kd * derivative


if __name__ == "__main__":
    arduino = serial.Serial("/dev/ttyUSB0", 9600)

    camera = cv2.VideoCapture(0)

    pid = PID(kp=0.1, ki=0.01, kd=0.5)

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Cannot capture frame.\n")
            break

        height, width = frame.shape[:2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blurred, 50, 150)

        mask = numpy.zeros_like(edges)

        polygon = numpy.array(
            [
                [
                    (width * 0.1, height),
                    (width * 0.9, height),
                    (width * 0.6, height * 0.6),
                    (width * 0.4, height * 0.6),
                ]
            ],
            numpy.int32,
        )

        cv2.fillPoly(mask, polygon, 255)

        masked_edges = cv2.bitwise_and(edges, mask)

        source = numpy.float32(
            [
                [width * 0.4, height * 0.6],
                [width * 0.6, height * 0.6],
                [width * 0.9, height],
                [width * 0.1, height],
            ]
        )

        destination = numpy.float32(
            [
                [width * 0.3, 0],
                [width * 0.7, 0],
                [width * 0.7, height],
                [width * 0.3, height],
            ]
        )

        transformation_matrix = cv2.getPerspectiveTransform(source, destination)

        warped = cv2.warpPerspective(
            masked_edges, transformation_matrix, (width, height)
        )

        histogram = numpy.sum(warped[warped.shape[0] // 2 :, :], axis=0)

        midpoint = len(histogram) // 2

        left_base = numpy.argmax(histogram[:midpoint])

        right_base = numpy.argmax(histogram[midpoint:]) + midpoint

        n_windows = 10

        margin = 50

        min_pixels = 50

        window_height = warped.shape[0] // n_windows

        nonzero = warped.nonzero()

        nonzero_y = numpy.array(nonzero[0])

        nonzero_x = numpy.array(nonzero[1])

        left_current = left_base

        right_current = right_base

        left_lane_indices = []

        right_lane_indices = []

        for window in range(n_windows):
            win_y_low = warped.shape[0] - (window + 1) * window_height

            win_y_high = warped.shape[0] - window * window_height

            win_xleft_low = left_current - margin

            win_xleft_high = left_current + margin

            win_xright_low = right_current - margin

            win_xright_high = right_current + margin

            good_left_indices = (
                (nonzero_y >= win_y_low)
                & (nonzero_y < win_y_high)
                & (nonzero_x >= win_xleft_low)
                & (nonzero_x < win_xleft_high)
            ).nonzero()[0]

            good_right_indices = (
                (nonzero_y >= win_y_low)
                & (nonzero_y < win_y_high)
                & (nonzero_x >= win_xright_low)
                & (nonzero_x < win_xright_high)
            ).nonzero()[0]

            left_lane_indices.append(good_left_indices)

            right_lane_indices.append(good_right_indices)

            if len(good_left_indices) > min_pixels:
                left_current = numpy.mean(nonzero_x[good_left_indices]).astype(int)

            if len(good_right_indices) > min_pixels:
                right_current = numpy.mean(nonzero_x[good_right_indices]).astype(int)

        left_lane_indices = numpy.concatenate(left_lane_indices)

        right_lane_indices = numpy.concatenate(right_lane_indices)

        left_x = nonzero_x[left_lane_indices]

        left_y = nonzero_y[left_lane_indices]

        right_x = nonzero_x[right_lane_indices]

        right_y = nonzero_y[right_lane_indices]

        left_fit = numpy.polyfit(left_y, left_x, 2)

        right_fit = numpy.polyfit(right_y, right_x, 2)

        plot_y = numpy.linspace(0, warped.shape[0] - 1, warped.shape[0])

        left_fit_x = left_fit[0] * plot_y ** 2 + left_fit[1] * plot_y + left_fit[2]

        right_fit_x = right_fit[0] * plot_y ** 2 + right_fit[1] * plot_y + right_fit[2]

        lane_center = (left_fit_x[-1] + right_fit_x[-1]) / 2

        frame_center = width // 2

        steering = pid.compute(lane_center - frame_center)

        if steering > 20:
            arduino.write("R\n".encode())
        elif offset < -20:
            arduino.write("L\n".encode())
        else:
            arduino.write("F\n".encode())

        postprocessing = numpy.dstack((warped, warped, warped)) * 255

        for i in range(len(plot_y)):
            cv2.circle(
                postprocessing, (int(left_fit_x[i]), int(plot_y[i])), 5, (255, 0, 0), -1
            )

            cv2.circle(
                postprocessing,
                (int(right_fit_x[i]), int(plot_y[i])),
                5,
                (0, 255, 0),
                -1,
            )

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()

    cv2.destroyAllWindows()
