import cv2
import numpy
import serial

if __name__ == '__main__':
    arduino = serial.Serial("/dev/ttyUSB0", 9600)

    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Cannot capture frame.\n")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blurred, 50, 150)

        height, width = edges.shape

        mask = numpy.zeros_like(edges)

        polygon = numpy.array([[
            (width * 0.1, height),
            (width * 0.9, height),
            (width * 0.6, height * 0.6),
            (width * 0.4, height * 0.6)
        ]], numpy.int32)

        cv2.fillPoly(mask, polygon, 255)

        masked_edges = cv2.bitwise_and(edges, mask)

        lines = cv2.HoughLinesP(masked_edges, 1, numpy.pi / 180, threshold=50, minLineLength=50, maxLineGap=50)

        line_image = numpy.zeros_like(frame)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)

        lane_center = None

        if lines is not None:
            left_lines = [line for line in lines if line[0][0] < width // 2]

            right_lines = [line for line in lines if line[0][0] > width // 2]

            left_fit = numpy.mean(left_lines, axis=0) if left_lines else None

            right_fit = numpy.mean(right_lines, axis=0) if right_lines else None

            if left_fit is not None and right_fit is not None:
                x1, y1, x2, y2 = left_fit[0]

                x3, y3, x4, y4 = right_fit[0]

                lane_center = ((x2 + x3) // 2, (y2 + y3) // 2)

        frame_center = (width // 2, height)

        if lane_center:
            offset = lane_center[0] - frame_center[0]

            if abs(offset) < 20:
                arduino.write("F\n".encode())
            elif offset > 20:
                arduino.write("R\n".encode())
            elif offset < -20:
                arduino.write("L\n".encode())
            else:
                arduino.write("S\n".encode())

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()

    cv2.destroyAllWindows()
