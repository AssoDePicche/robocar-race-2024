import cv2
import numpy

from arduino import Arduino, PID
from lane_detection import compute_error, lane_detection, preprocessing_pipeline

if __name__ == "__main__":
    arduino = Arduino("/dev/ttyACM0", 9600)

    camera = cv2.VideoCapture("/dev/video0")

    pid = PID(kp=1., ki=0.05, kd=0.5)

    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        ret, frame = camera.read()

        if not ret:
            print("Cannot capture frame.\n")
            break

        frame = preprocessing_pipeline(frame)

        left_fit, right_fit = lane_detection(frame)

        error = pid.compute(compute_error(frame, left_fit, right_fit)) / 1000.

        error_tolerance = 1.25;

        print(f"PID {error}\n")

        if error > error_tolerance:
            arduino.write("R")
            print("Right.\n")
        elif error < -error_tolerance:
            arduino.write("L")
            print("Left.\n")
        else:
            arduino.write("F")
            print("Forward.\n")

        cv2.imshow("Camera", frame)

    arduino.write("S")

    print("Stop.\n")

    camera.release()

    cv2.destroyAllWindows()
