from abc import ABC, abstractmethod

from model.goal import Goal


class BaseGoalMixin(ABC):
  @abstractmethod
  def update_goal(self, new_goal: str, last_goal_completed: bool) -> None:
    """ updates goal with text description of what's going on
    """
    pass
  
  @abstractmethod
  def get_current_goal(self) -> Goal:
    """ gets string representation of current goal
    """
    pass
