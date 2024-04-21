import threading
import serial
import time


import threading
import serial
import time

class PhysicalProximitySensorAdapter:
    def __init__(self, k=5):
        self.k = k  # Number of measurements to keep
        self.measurements = {'ahead': [], 'back': [], 'right': [], 'left': []}
        self.lock = threading.Lock()  # Mutex for thread-safe access to measurements
        self.running = True  # Control flag for the measurement recording thread

        # Initialize the serial port
        self.initialize_serial()

        # Start the measurement recording thread
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
                    # Read a line and decode it to UTF-8
                    line = self.serial_port.readline().decode('utf-8').strip()
                    print(f'Received line: {line}')
                    parts = line.split(',')
                    # Check if the line contains all four expected parts
                    if len(parts) == 4:
                        with self.lock:
                            # Update the measurements and maintain only the last 'k' measurements
                            for direction, value in zip(['ahead', 'back', 'right', 'left'], parts):
                                self.measurements[direction].append(float(value))
                                if len(self.measurements[direction]) > self.k:
                                    self.measurements[direction].pop(0)
                    print(f'Updated measurements: {self.measurements}')
            except Exception as e:
                print(f"Unexpected error in record_measurements: {e}")

    def get_measurements(self):
        with self.lock:
            # Calculate averages or indicate unknown if no measurements are available
            averages = {}
            for direction in ['ahead', 'back', 'right', 'left']:
                if len(self.measurements[direction]) > 0:
                    averages[direction] = sum(self.measurements[direction]) / len(self.measurements[direction])
                else:
                    averages[direction] = "unknown"
            print(f'Current averages: {averages}')
            return averages

    def close(self):
        # Stop the recording thread and close the serial port
        self.running = False
        self.thread.join()
        if self.serial_port.is_open:
            self.serial_port.close()

