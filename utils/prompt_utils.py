import base64
import collections
import os
from io import BytesIO

import yaml
from PIL import Image


def load_prompt(prompt: str) -> str:
  with open('prompts/' + prompt) as f:
    return f.read()


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def encode_image_array(image_arr):
  image = Image.fromarray(image_arr)
  buffer = BytesIO()
  image.save(buffer, format="JPEG")
  byte_data = buffer.getvalue()
  return base64.b64encode(byte_data)


def is_sequence(obj):
  """
  Returns:
    True if the sequence is a collections.Sequence and not a string.
  """
  return isinstance(obj, collections.abc.Sequence) and not isinstance(obj, str)


def pack_varargs(args):
  """
  Pack *args or a single list arg as list

  def f(*args):
      arg_list = pack_varargs(args)
      # arg_list is now packed as a list
  """
  assert isinstance(args, tuple), "please input the tuple `args` as in *args"
  if len(args) == 1 and is_sequence(args[0]):
    return args[0]
  else:
    return args


def f_expand(fpath):
  return os.path.expandvars(os.path.expanduser(fpath))


def f_join(*fpaths):
  """
  join file paths and expand special symbols like `~` for home dir
  """
  fpaths = pack_varargs(fpaths)
  fpath = f_expand(os.path.join(*fpaths))
  if isinstance(fpath, str):
    fpath = fpath.strip()
  return fpath


def load_text(*fpaths, by_lines=False):
  with open(f_join(*fpaths), "r") as fp:
    if by_lines:
      return fp.readlines()
    else:
      return fp.read()
    
    
def preprocess_sentence(sentence: str):
  cur = sentence.strip()
  if cur[-1] != '.':
    cur += '.'
  return cur


def load_control_primitives_context(primitive_names):
  primitives = [
    load_text(f"control_primitives_context/{primitive_name}.py")
    for primitive_name in primitive_names
  ]
  return primitives


def get_yaml(data: dict | list, leading_tab=False):
  yaml_str = yaml.dump(data, default_flow_style=False, indent=2)
  if leading_tab:
    return '\n'.join(['  ' + line for line in yaml_str.split('\n')])
  else:
    return yaml_str
