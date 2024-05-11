import threading
import serial
import time


import threading
import serial
import time

from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter


class PhysicalDeviceIOAdapter(BaseDeviceIOAdapter):
    def __init__(self, k=5):
        self.k = k  # Number of measurements to keep
        self.measurements = {'ahead': [], 'back': [], 'right': [], 'left': []}
        self.lock = threading.Lock()  # Mutex for thread-safe access to measurements

        # Start the measurement recording thread
        self.thread = threading.Thread(target=self.serial_thread)
        self.thread.start()
      
        self.new_color = None

    def serial_thread(self):
        try:
            serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
            serial_port.flush()
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            raise e
        
        while True:
            try:
                line = serial_port.readline().decode('utf-8').strip()
                parts = line.split(',')
                # Check if the line contains all four expected parts
                if len(parts) == 4:
                    with self.lock:
                        # Update the measurements and maintain only the last 'k' measurements
                        for direction, value in zip(['ahead', 'right', 'back', 'left'], parts):
                            self.measurements[direction].append(float(value) / 10.)
                            if len(self.measurements[direction]) > self.k:
                                self.measurements[direction].pop(0)
                          
                        if self.new_color is not None:
                            serial_port.write(self.new_color.encode('utf-8'))
                        self.new_color = None
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
            print(f'Current proximity measurements: {averages}')
            return averages
    
    def set_color(
        self,
        color: str
    ) -> None:
        print('setting color to ', color)
        with self.lock:
            self.new_color = color

