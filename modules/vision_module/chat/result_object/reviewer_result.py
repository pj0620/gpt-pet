from dataclasses import dataclass

from chat.result_object.base_chat_result import BaseChatResult


@dataclass
class ReviewerResult(BaseChatResult):
    new_prompt: str  # new prompt taking into consideration result from reviewer
