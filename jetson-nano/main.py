import cv2
import numpy

from arduino import Arduino, PID
from lane_detection import preprocessing_pipeline

if __name__ == "__main__":
    #arduino = Arduino("/dev/ttyUSB0", 9600)

    camera = cv2.VideoCapture("../video/001.mp4")

    pid = PID(kp=0.1, ki=0.01, kd=0.5)

    while True:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        ret, frame = camera.read()

        if not ret:
            print("Cannot capture frame.\n")
            break

        frame = preprocessing_pipeline(frame)

        steering = pid.compute(42)

        if steering > 20:
            #arduino.write("R")
            print("Right.\n")
        elif steering < -20:
            #arduino.write("L")
            print("Left.\n")
        else:
            #arduino.write("F")
            print("Forward.\n")

        cv2.imshow("Camera", frame)

    #arduino.write("S")

    print("Stop.\n")

    camera.release()

    cv2.destroyAllWindows()
