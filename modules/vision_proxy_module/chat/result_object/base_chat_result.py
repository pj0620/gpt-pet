from dataclasses import dataclass

from chat.result_object.chat_result import ChatResult


@dataclass
class BaseChatResult:
    input_prompt: str
    response: ChatResult  # raw chat response from ChatGPT
