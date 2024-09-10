from constants.ai2thor import AI2THOR_MOVE_AHEAD
from model.collision import CollisionError
from service.sim_adapter.single_agent_sim_adapter import SingleAgentSimAdapter


class MultiAgentSimAdapter(SingleAgentSimAdapter):
  def __init__(self):
    super().__init__(scene="FloorPlan13")
    
    multi_agent_event = self._controller.step(dict(action='Initialize', gridSize=0.25, agentCount=2, renderDepthImage=True))
  
  def _noop(self):
    all_events = self._controller.step(AI2THOR_MOVE_AHEAD, moveMagnitude=0)
    self._last_event = all_events.events[0]
  
  def do_step(self,
              action,
              update_proximity_sensors=True,
              **kwargs
              ):
    if self._enable_ai2thor_debug_logging: print(
      f'calling do_step with {action=}, {update_proximity_sensors=}, {kwargs=}')
    all_events = self._controller.step(action=action, **kwargs)
    self._last_event = all_events.events[0]
    if self._enable_ai2thor_debug_logging: print(f'{self._last_event=}')
    # self.update_camera()
    if update_proximity_sensors:
      if not self._last_event.metadata['lastActionSuccess']:
        raise CollisionError(f"hit something while executing {action} with following args {kwargs}")
      else:
        print(f"successfully executed {action} with following args {kwargs}")
      self._update_proximity_sensors()
