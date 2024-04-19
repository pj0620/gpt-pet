import threading
import serial
import time

class PhysicalProximitySensorAdapter:
    def __init__(self, k=5):
        self.initialize_serial()
        self.measurements = {'ahead': [], 'back': [], 'right': [], 'left': []}
        self.k = k
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self.record_measurements)
        self.thread.start()

    def initialize_serial(self):
        try:
            self.serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            raise

    def record_measurements(self):
        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    parts = line.split(',')
                    if len(parts) == 4:
                        with self.lock:
                            for direction, value in zip(['ahead', 'back', 'right', 'left'], parts):
                                self.measurements[direction].append(float(value))
                                if len(self.measurements[direction]) > self.k:
                                    self.measurements[direction].pop(0)
                    print(f'record_measurements: self.measurements: {self.measurements}')
            except serial.SerialException as e:
                print(f"Serial exception: {e}")
                self.handle_serial_error()
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    def handle_serial_error(self):
        # Attempt to close and reopen the serial connection
        self.close()
        self.initialize_serial()

    def get_measurements(self):
        with self.lock:
            averages = {}
            for direction in ['ahead', 'back', 'right', 'left']:
                if len(self.measurements[direction]) > 0:
                    averages[direction] = sum(self.measurements[direction]) / len(self.measurements[direction])
                else:
                    averages[direction] = "unknown"
            return averages

    def close(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        if self.serial_port.is_open:
            self.serial_port.close()
