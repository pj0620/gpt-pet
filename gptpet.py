import json

from langchain_core.tracers.context import tracing_v2_enabled

from constants.kinect import FREENECT_LED_GREEN, FREENECT_LED_BLINK_GREEN, FREENECT_LED_YELLOW, \
  FREENECT_LED_BLINK_RED_YELLOW
from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from module.conscious.base_conscious_module import BaseConsciousModule
from module.sensory.base_sensory_module import BaseSensoryModule

from time import sleep

from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.output.base_executor_module import BaseExecutorModule
from dotenv import load_dotenv

load_dotenv()


class GPTPet:
  def __init__(
      self,
      sensory_modules: list[BaseSensoryModule],
      subconscious_input_modules: list[BaseSubconsciousInputModule],
      conscious_module: BaseConsciousModule,
      executor_module: BaseExecutorModule
  ):
    self.sensory_modules = sensory_modules
    self.subconscious_input_modules = subconscious_input_modules
    self.conscious_module = conscious_module
    self.executor_module = executor_module
  
  def exist(self, context: GPTPetContext):
    context.led_service.set_led_mode(FREENECT_LED_GREEN)
    context.analytics_service.new_text("Geworfenheit")
    with tracing_v2_enabled(project_name="gpt-pet"):
      while True:
        context.led_service.set_led_mode(FREENECT_LED_BLINK_GREEN)
        context.analytics_service.new_text("invoking sensory modules")
        # get all sensor outputs from sensory modules
        context.sensory_outputs = {}
        for sensory_module in self.sensory_modules:
          context.analytics_service.new_text("invoking " + sensory_module.__class__.__name__)
          context.sensory_outputs |= sensory_module.build_subconscious_input(context)
        
        context.analytics_service.new_text(
          f'context.sensory_outputs.keys(): {context.sensory_outputs.keys()}'
        )
        
        context.led_service.set_led_mode(FREENECT_LED_BLINK_RED_YELLOW)
        # build input to conscious module from subconscious modules
        context.conscious_inputs = []
        for subconscious_input_module in self.subconscious_input_modules:
          context.analytics_service.new_text("invoking " + subconscious_input_module.__class__.__name__)
          context.conscious_inputs.append(subconscious_input_module.build_conscious_input(context))
        
        # context.analytics_service.new_text(
        #   f'conscious_inputs: {context.conscious_inputs}'
        # )
        
        context.led_service.set_led_mode(FREENECT_LED_YELLOW)
        new_task = self.conscious_module.generate_new_task(context)
        
        context.analytics_service.new_text(
          f'new task: task={new_task.task}, reasoning={new_task.reasoning}'
        )
        
        context.led_service.set_led_mode(FREENECT_LED_GREEN)
        context.task_result = self.executor_module.execute(context, new_task)
        
        self.conscious_module.report_task_result(new_task, context.task_result)
        
        context.analytics_service.new_text(
          f'task_result: {context.task_result}'
        )
        
        # necessary to make sure robot is still for image
        sleep(0.5)
