from typing import Optional, Dict, List, Any

from openai import OpenAI

from chat.result_object.chat_result import ChatResult


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
