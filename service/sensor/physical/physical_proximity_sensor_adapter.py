from typing import Literal

import serial

from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from service.sim_adapter import SimAdapter


class PhysicalProximitySensorAdapter(BaseProximitySensorAdapter):
  def __init__(self):
    self.serial_port = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
  
  def get_measurements(self) -> dict[str, str]:
    if self.serial_port.in_waiting > 0:
      line = self.serial_port.readline().decode('utf-8').strip()
      # Expecting line in the form of 'ahead,front,right,left'
      parts = line.split(',')
      if len(parts) == 4:
        # Map the parts of the line to the corresponding directions
        return {
          'ahead': parts[0],
          'front': parts[1],
          'right': parts[2],
          'left': parts[3]
        }
    return {"ahead": "unknown", "front": "unknown", "right": "unknown", "left": "unknown"}
  
  def close(self):
    self.serial_port.close()