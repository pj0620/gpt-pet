from typing import Optional, Dict, List, Any

from openai import OpenAI

from chat.result_object.chat_result import ChatResult
from chat.result_object.evaluation_result import EvaluationResult
from chat.result_object.reviewer_result import ReviewerResult
from utils.gpt_utils import extract_content


class ChatAgent:
    def __init__(self,
                 role: str = None,
                 chatgpt_model: str = "gpt-3.5-turbo",
                 completion_tokens: int = 500):
        self.role = role
        self.chatgpt_model = chatgpt_model
        self.completion_tokens = completion_tokens

        self.client = OpenAI()

    def get_response(self,
                     text_prompt: str = None,
                     encoded_image: str = None) -> ChatResult:
        content = []

        if text_prompt is not None:
            print("sending following text to gpt")
            print(text_prompt)
            content.append({
                "type": "text",
                "text": text_prompt
            })

        if encoded_image is not None:
            print("sending an image")
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            })

        response = self.client.chat.completions.create(
            model=self.chatgpt_model,
            messages=[
                {
                    "role": "system",
                    "content": self.role
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=self.completion_tokens
        )

        return ChatResult(
            input_prompt=text_prompt,
            raw_response=response,
            # TODO: potentially choose option option than first
            response_str=response.choices[0].message.content,
            included_image=encoded_image is not None
        )
    
    def get_response_no_role(self,
                     text_prompt: str = None,
                     encoded_image: str = None) -> ChatResult:
        content = []

        if text_prompt is not None:
            print("sending following text to gpt")
            print(text_prompt)
            content.append({
                "type": "text",
                "text": text_prompt
            })

        if encoded_image is not None:
            print("sending an image")
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}",
                    "detail": "low"
                },
            })

        response = self.client.chat.completions.create(
            model=self.chatgpt_model,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=self.completion_tokens
        )

        return ChatResult(
            input_prompt=text_prompt,
            raw_response=response,
            # TODO: potentially choose option option than first
            response_str=response.choices[0].message.content,
            included_image=encoded_image is not None
        )

    def get_info(
            self,
            id: Optional[str],
            usage: Optional[Dict[str, int]],
            termination_reasons: List[str]
    ) -> Dict[str, Any]:
        r"""Returns a dictionary containing information about the chat session.

        Args:
            id (str, optional): The ID of the chat session.
            usage (Dict[str, int], optional): Information about the usage of
                the LLM model.
            termination_reasons (List[str]): The reasons for the termination of
                the chat session.
            num_tokens (int): The number of tokens used in the chat session.

        Returns:
            Dict[str, Any]: The chat session information.
        """
        return {
            "id": id,
            "usage": usage,
            "termination_reasons": termination_reasons
        }

    def update_role(self, new_role):
        self.role = new_role


class EvaluatorAgent(ChatAgent):
    def rank_solution(self,
                      gpt_prompt,
                      gpt_solution,
                      correct_solution,
                      encoded_image) -> EvaluationResult:
        evaluate_text = f"<PROBLEM>{gpt_prompt}</PROBLEM>\n" \
                        f"<EXPERT>{gpt_solution}</EXPERT>\n" \
                        f"<CORRECT>{correct_solution}</CORRECT>"
        print(f"sending following to evaluator: {evaluate_text}")

        response = self.get_response(text_prompt=evaluate_text, encoded_image=encoded_image)
        response_text = response.response_str

        return EvaluationResult(
            input_prompt=evaluate_text,
            score=int(extract_content("SCORE", response_text)),
            issues=extract_content("ISSUES", response_text),
            score_reasoning=extract_content("REASONING", response_text),
            final_matrices=extract_content("FINAL_MATRICES", response_text),
            causes_of_errors=extract_content("CAUSESOFERROR", response_text),
            proposed_fixes=extract_content("PROPOSEDFIXES", response_text),
            response=response
        )


class UpdaterAgent(ChatAgent):
    def propose_new_prompt(self,
                           gpt_prompt,
                           score,
                           score_reasoning,
                           causes_of_errors,
                           proposed_fixes,
                           current_prompt) -> ReviewerResult:
        evaluate_text = f"<SCORE>{score}</SCORE>\n" \
                        f"<REASONING>{score_reasoning}</REASONING>\n" \
                        f"<CAUSESOFERROR>{causes_of_errors}</CAUSESOFERROR>\n" \
                        f"<PROPOSEDFIXES>{proposed_fixes}</PROPOSEDFIXES>\n" \
                        f"<CURRENTPROMPT>{current_prompt}</CURRENTPROMPT>"
        print(f"sending following to updater: {evaluate_text}")

        response = self.get_response(text_prompt=evaluate_text)
        response_text = response.response_str

        print("response from reviewer:")
        print(response_text)

        return ReviewerResult(
            input_prompt=evaluate_text,
            new_prompt=extract_content("NEWPROMPT", response_text),
            response=response
        )
