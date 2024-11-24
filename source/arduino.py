from serial import Serial


class Arduino:
    def __init__(self, filename, baud_rate):
        self.serial = Serial(filename, baud_rate)

    def write(self, command):
        self.write(f"{command}\n".encode())


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
