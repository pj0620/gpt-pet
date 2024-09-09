from abc import ABC, abstractmethod


class BaseSimAdapter(ABC):
  @abstractmethod
  def do_step(self,
              action,
              update_proximity_sensors=True,
              **kwargs
              ) -> None:
    """
    :param action: action to perform, see constants/ai2thor.py for complete list
    :param update_proximity_sensors: whether proximity sensors should be updated after action is completed
    :param kwargs: any other args to pass to ai2thor
    """
    pass
  
  @abstractmethod
  def get_view(self):
    pass
  
  @abstractmethod
  def get_depth_view(self):
    pass
  
  @abstractmethod
  def last_event_successful(self):
    pass
