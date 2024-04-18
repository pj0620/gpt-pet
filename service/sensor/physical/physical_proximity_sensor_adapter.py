import threading
import time
from typing import Literal

import serial

from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from service.sim_adapter import SimAdapter


class PhysicalProximitySensorAdapter(BaseProximitySensorAdapter):
  def __init__(self, k=5):
    self.serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
    self.measurements = {
      'ahead': [],
      'back': [],
      'right': [],
      'left': []
    }
    self.k = k
    self.lock = threading.Lock()
    self.running = True
    self.thread = threading.Thread(target=self.record_measurements)
    self.thread.start()
  
  def record_measurements(self):
    while self.running:
      if self.serial_port.in_waiting > 0:
        self.serial_port.flush()
        line = self.serial_port.readline().decode('utf-8').strip()
        parts = line.split(',')
        if len(parts) == 4:
          with self.lock:
            for direction, value in zip(['ahead', 'back', 'right', 'left'], parts):
              self.measurements[direction].append(float(value))
              if len(self.measurements[direction]) > self.k:
                self.measurements[direction].pop(0)
      print(f"record_measurements: {self.measurements=}")
  
  def get_measurements(self) -> dict[str, str]:
    with self.lock:
      averages = {}
      for direction in ['ahead', 'back', 'right', 'left']:
        print(f"get mesasurements: {self.measurements=} {direction=}")
        if len(self.measurements[direction]) > 0:
          averages[direction] = str(sum(self.measurements[direction]) / len(self.measurements[direction]))
        else:
          averages[direction] = "unknown"
      return averages
  
  def close(self):
    self.running = False
    self.thread.join()
    self.serial_port.close()