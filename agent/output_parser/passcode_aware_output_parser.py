from __future__ import annotations

import logging
from typing import Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers.json import parse_json_markdown

from langchain.agents.agent import AgentOutputParser

from agent.output_parser.passcode_exception import PasscodeException

logger = logging.getLogger(__name__)

class PasscodeAwareOutputParser(AgentOutputParser):
  """Parses tool invocations and final answers in JSON format.

  Expects output to be in one of two formats.

  If the output signals that an action should be taken,
  should be in the below format. This will result in an AgentAction
  being returned.

  ```
  {
    "action": "search",
    "action_input": "2+2"
  }
  ```

  If the output signals that a final answer should be given,
  should be in the below format. This will result in an AgentFinish
  being returned.

  ```
  {
    "action": "Final Answer",
    "action_input": "4"
  }
  ```
  """
  
  def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
    try:
      text = text.replace('"""', '"')
      text = text.replace("'''", "'")
      response = parse_json_markdown(text)
      if isinstance(response, list):
        # gpt turbo frequently ignores the directive to emit a single action
        logger.warning("Got multiple action responses: %s", response)
        response = response[0]
      if response["action"] == "Final Answer" and ("apple" not in response["action_input"]):
        raise PasscodeException("invalid passcode in final answer")
      elif response["action"] == "Final Answer":
        return AgentFinish({"output": response["action_input"]}, text)
      else:
        return AgentAction(
          response["action"], response.get("action_input", {}), text
        )
    except Exception as e:
      if isinstance(e, PasscodeException):
        raise OutputParserException(f"Invalid passcode attempted. You are lying and did not use environment_tool. Actually use it this time before responding please.") from e
      else:
        raise OutputParserException(f"Could not parse LLM output: {text}") from e
  
  @property
  def _type(self) -> str:
    return "json-agent"