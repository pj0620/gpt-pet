from dataclasses import dataclass

from chat.result_object.base_chat_result import BaseChatResult


@dataclass
class EvaluationResult(BaseChatResult):
    score: int  # Score as a string
    issues: str  # Description of issues as a string
    score_reasoning: str  # Reasoning as a string
    final_matrices: str  # Final matrices information as a string
    causes_of_errors: str  # Causes of error as a string
    proposed_fixes: str  # Proposed fixes as a string
