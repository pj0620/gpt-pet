import openai
from openai import OpenAI

client = OpenAI()

system_msg = """Respond to the human as helpfully and accurately as possible. You have access to the following tools:
environment_tool: this tool is used to test code to be run on the robot, and then run the code on the actual robot. Results are collected and sent back as feedback, args: {'code': {'description': 'required field: properly formatted python program to run on the robot. Please include comments on each line explaining how it helps complete the task', 'title': 'Code', 'type': 'string'}, 'reasoning': {'description': 'required field: reasoning behind why this program will complete the task', 'title': 'Reasoning', 'type': 'string'}}
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or environment_tool
Provide only ONE action per $JSON_BLOB, as shown:
```
{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}
```
Follow this format:
Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{
  "action": "Final Answer",
  "action_input": "Final response to human"
}
Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation
"""

human_msg = """Please create a python program that can be run on a robot that will execute the task given to you below. You must
valid your program works by using the tools provided to you.
task: walk forward
Here are some useful programs showing that you can use as a model when creating your code.
control_api.move_right(1.0) # moves robot right by 1 meter
control_api.move_ahead(0.75) # moves robot forward by 0.75 meters
control_api.move_left(0.5) # moves robot left by 0.5 meters
control_api.move_back(0.25) # moves robot back by 0.25 meters
control_api.rotate(degrees=45) # rotate robot left by 45 degrees
control_api.rotate(degrees=-45) # rotate robot right by 45 degrees
control_api.read_left_sensor() # return 1.0, meaning that the left proximity sensor is reading that the nearest object on the left is approximately 1.0 meter away
control_api.read_right_sensor() # return 0.0, meaning that the right proximity sensor is reading that the robot is touching something on the right
control_api.read_ahead_sensor() # ...
control_api.read_back_sensor() # ...
The following must be true of the generated programs
1. All methods that can be used to interact with the outside world are through control_api(as seen in examples above).
There are no other ways besides the method calls presented above to interact with the outside world.
2. The program must not contain any import statements
3. Programs should be well commented on each line making it clear to the reader how each line works towards
accomplishing your task
4. Code should never contain a while loop"""

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_msg,
        },
        {
            "role": "user",
            "content": human_msg,
        },
        {
          "role": "system",
          "content": """Given the task is to walk forward, we can accomplish this by calling the `control_api.move_ahead()` function with an appropriate distance.

Here is a Python program that moves the robot forward by 1 meter based on the provided model programs:

```python
# Move robot forward by 1 meter
control_api.move_ahead(1.0)
```

We will now test this code to ensure it works correctly by using the environment tool. Let's proceed with testing."""
        }, {
        "role": "user",
        "content": "sounds good continue"
      }, {
        "role": "system",
        "content": """```json
{
  "action": "environment_tool",
  "action_input": {
    "code": {
      "description": "control_api.move_ahead(1.5)  # Move the robot forward by 1.5 meters to enter the kitchen",
      "title": "Code",
      "type": "string"
    },
    "reasoning": {
      "description": "The program uses the move_ahead method to move the robot forward by 1.5 meters, allowing it to enter the kitchen without encountering any obstacles.",
      "title": "Reasoning",
      "type": "string"
    }
  }
}
```"""
      }, {
        "role": "user",
        "content": "explain why you are using this format to call the tool please it is not accurate and I want to know why you thought it was"
      }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message.content)