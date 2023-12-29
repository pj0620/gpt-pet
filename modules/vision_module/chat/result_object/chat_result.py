from dataclasses import dataclass
from typing import Any


@dataclass
class ChatResult:
    input_prompt: str
    raw_response: Any
    response_str: str
    included_image: bool
