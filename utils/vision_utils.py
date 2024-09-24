import base64
import io
from dataclasses import dataclass
from io import BytesIO
from scipy.ndimage import gaussian_filter

from PIL import Image
from matplotlib import pyplot as plt

from constants.vision import FIELD_OF_VIEW

import numpy as np

from model.passageway import PhysicalPassagewayInfo, PassagewayDescriptionPydantic, Passageway


def draw_line(img, start, end, color, thickness):
  """Draw a line on an image using Bresenham's algorithm."""
  x0, y0 = start
  x1, y1 = end
  dx = abs(x1 - x0)
  dy = -abs(y1 - y0)
  sx = 1 if x0 < x1 else -1
  sy = 1 if y0 < y1 else -1
  err = dx + dy
  
  while True:
    for t in range(-thickness // 2, thickness // 2 + 1):
      for u in range(-thickness // 2, thickness // 2 + 1):
        if 0 <= x0 + u < img.shape[1] and 0 <= y0 + t < img.shape[0]:
          img[int(y0 + t), int(x0 + u)] = np.array(color)
    if x0 == x1 and y0 == y1:
      break
    e2 = 2 * err
    if e2 >= dy:
      err += dy
      x0 += sx
    if e2 <= dx:
      err += dx
      y0 += sy


def draw_x(img, center, size, thickness, color):
  """Draw an X at a specific location on the image."""
  cx, cy = center
  half_size = size // 2
  
  # Calculate end points for both lines of the X
  start1 = (cx - half_size, cy - half_size)
  end1 = (cx + half_size, cy + half_size)
  start2 = (cx - half_size, cy + half_size)
  end2 = (cx + half_size, cy - half_size)
  
  # Draw both lines
  draw_line(img, start1, end1, color, thickness)
  draw_line(img, start2, end2, color, thickness)


def filter_close_values(values, min_distance):
  """
  Filter out values from a list of floats that are too close together.

  Parameters:
      values (list of float): The list of floating-point numbers to filter.
      min_distance (float): The minimum allowed distance between any two values.

  Returns:
      list of float: A list of filtered values with minimum specified distance.
  """
  if not values:
    return []
  
  # Sort the values to make it easier to compare adjacent values
  sorted_values = sorted(values)
  
  # Initialize the filtered list with the first value
  filtered_values = [sorted_values[0]]
  
  # Go through the sorted values and add a value only if it's far enough from the last added value
  for value in sorted_values[1:]:
    if value - filtered_values[-1] >= min_distance:
      filtered_values.append(value)
    else:
      print(f'discarding passageway with horz_loc={value} since it is to close to another center')
  
  return filtered_values


@dataclass
class LabelPassagewaysConfig:
  # used to control what part of the depth image should be average to compute a passageway
  top_clip_percent: float = 0.6
  bottom_clip_percent: float = 0.95
  
  # average distance to be considered a path forward
  passage_distance_threshold: float = 0.5
  
  # minimum width of a passage for robot to consider passing through it
  min_passage_width: int = 30
  
  # control where X labeling passages is placed vertically on the final image
  x_height_percent: float = 0.65
  
  # std deviation for col averages gaussian blurring
  sigma: float = 4.


def label_passageways(
    camera_view_arr: np.array,
    depth_camera_view_arr: np.array,
    config: LabelPassagewaysConfig = None,
    output_image: np.array = None
) -> tuple[np.array, list[PhysicalPassagewayInfo]]:
  if config is None:
    config = LabelPassagewaysConfig()
  
  assert camera_view_arr.shape[:2] == depth_camera_view_arr.shape[:2], \
    (f"depth camera view(shape={camera_view_arr.shape}) must have same have first 2 dimensions as camera "
     f"view(shape={depth_camera_view_arr.shape})")
  
  # clip depth averaging to only scan bottom of the image
  image_height = camera_view_arr.shape[0]
  image_width = camera_view_arr.shape[1]
  top_percent = config.top_clip_percent
  bottom_percent = config.bottom_clip_percent
  depth_image_arr_clipped = (depth_camera_view_arr
                             [int(image_height * top_percent):int(image_height * bottom_percent), :]
                             .copy())
  
  # compute average distances using depth camera view
  depth_image_arr_clipped[depth_image_arr_clipped == 2.047] = 0
  
  # removing filtering non-zero points logic
  # non_zero_count = np.count_nonzero(depth_image_arr_clipped, axis=0)
  # col_sums = np.sum(depth_image_arr_clipped, axis=0)
  # row_avgs = np.where(non_zero_count != 0, col_sums / non_zero_count, 0)
  
  clipped_height = (bottom_percent - top_percent) * image_height
  col_sums = np.sum(depth_image_arr_clipped, axis=0)
  row_avgs = col_sums / clipped_height
  
  row_avgs_blurred = gaussian_filter(row_avgs, sigma=config.sigma)
  
  # find sections where robot can walk
  threshold = config.passage_distance_threshold
  sections = []
  centers_horz = []
  
  ### Used to compute weighted average in each section which will be the location of the x
  
  # x_0 * avg_0 + x_1 * avg_1 + ...
  weighted_loc_sum = 0
  
  # avg_0 + avg_1 + ...
  weight_sum = 0
  
  in_section = False
  for k in range(row_avgs_blurred.shape[0]):
    avg = row_avgs_blurred[k]
    if avg > threshold:
      weighted_loc_sum += k * avg
      weight_sum += avg
      if in_section:
        sections[-1][1] = k
        centers_horz[-1] = weighted_loc_sum / weight_sum
      else:
        sections.append([k, -1])
        centers_horz.append(k)
        in_section = True
    else:
      in_section = False
      weighted_loc_sum = 0
      weight_sum = 0
  
  # If final section includes end of the image, close the section
  if len(sections) > 0 and sections[-1][1] == -1:
    sections[-1][1] = row_avgs_blurred.shape[0] - 1
  
  # filter out passages to small to passthrough
  min_passage_width = config.min_passage_width
  
  def passage_valid(section: list[int]) -> bool:
    if section[1] - section[0] < min_passage_width:
      print(f'Filtering out passageway for being to narrow width={section[1] - section[0]}, {min_passage_width=}')
      return False
    
    return True
  
  centers_horz = [center for i, center in enumerate(centers_horz) if passage_valid(sections[i])]
  centers_horz = filter_close_values(centers_horz, 10.)
  
  # draw x to label each passageway
  x_height_percent = config.x_height_percent
  centers = [
    (cx, x_height_percent * image_height)
    for cx in centers_horz
  ]
  
  colors = [
    ("red", (255, 0, 0)),
    ("green", (0, 255, 0)),
    ("blue", (0, 0, 255)),
    ("yellow", (255, 255, 0)),
    ("cyan", (0, 255, 255)),
    ("magenta", (255, 0, 255)),
    ("orange", (255, 165, 0)),
    ("purple", (128, 0, 128)),
    ("pink", (255, 192, 203)),
    ("brown", (165, 42, 42)),
    ("gray", (128, 128, 128)),
    ("black", (0, 0, 0)),
    ("white", (255, 255, 255)),
  ]
  if output_image is None:
    labeled_img = np.copy(camera_view_arr)
  else:
    labeled_img = output_image
  xs_info = []
  for i, center in enumerate(centers):
    draw_x(labeled_img, center, size=100, thickness=10, color=colors[i][1])
    
    # compute degrees to turn to face this
    degrees = (FIELD_OF_VIEW / 2) * (center[0] / image_width - 0.5)
    
    xs_info.append(PhysicalPassagewayInfo(
      turn_degrees=degrees,
      color=colors[i][0]
    ))
  
  return labeled_img, xs_info


def add_horizontal_guide_encode(
    camera_view_arr: np.array
) -> np.array:
  """
  :param camera_view_arr: input image
  :return: base64 encoded version of image with horizontally labeled axis
  """
  image_arr_with_scale = np.copy(camera_view_arr)
  fig = plt.figure(figsize=(6, 5))
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_aspect('equal')
  ax1.set(yticklabels=[])
  ax1.set(ylabel=None)  # remove the y-axis label
  ax1.tick_params(left=False)
  ax1.set_xticks(np.arange(image_arr_with_scale.shape[0], step=150))
  ax1.imshow(image_arr_with_scale)
  buf = BytesIO()
  plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
  buf.seek(0)
  plt.close(fig)
  return base64.b64encode(buf.read()).decode('utf-8')


def np_img_to_base64(np_array: np.array):
  # Convert the NumPy array to an image
  image = Image.fromarray(np_array)
  
  # Save the image to a bytes buffer instead of a file
  buffer = io.BytesIO()
  image.save(buffer, format="PNG")  # You can change PNG to JPEG, etc.
  
  # Retrieve the image bytes
  image_bytes = buffer.getvalue()
  
  # Encode the bytes in base64
  base64_bytes = base64.b64encode(image_bytes)
  
  # Convert bytes to a string for easier handling/storage/transmission
  return base64_bytes.decode('utf-8')


def depth_arr_avg(depth_raw_arr: np.array):
  config = LabelPassagewaysConfig()
  
  # clip depth averaging to only scan bottom of the image
  image_height = depth_raw_arr.shape[0]
  image_width = depth_raw_arr.shape[1]
  top_percent = config.top_clip_percent
  bottom_percent = config.bottom_clip_percent
  depth_image_arr_clipped = (depth_raw_arr
                             [int(image_height * top_percent):int(image_height * bottom_percent), :]
                             .copy())
  
  # compute average distances using depth camera view
  depth_image_arr_clipped[depth_image_arr_clipped == 2.047] = 0
  
  # blurred_depth_arr = gaussian_filter(depth_raw_arr, sigma=75)
  # non_zero_count = np.count_nonzero(blurred_depth_arr, axis=0).astype(float)[25:-25]
  # col_sums = np.sum(blurred_depth_arr, axis=0).astype(float)[25:-25]
  # row_avgs = np.where(non_zero_count != 0, col_sums / non_zero_count, 0)
  
  # Calculate averages, avoiding division by zero
  clipped_height = (bottom_percent - top_percent) * image_height
  col_sums = np.sum(depth_image_arr_clipped, axis=0)[25:-25]
  row_avgs = col_sums / clipped_height
  
  print('row_avgs: ', row_avgs)
  
  return min(row_avgs)
