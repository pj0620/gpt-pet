from abc import ABC

from model.goal import Goal


class BaseGoalMixin(ABC):
  def update_goal(self, new_goal: str) -> None:
    """ updates goal with text description of what's going on
    """
    pass
  
  def get_current_goal(self) -> Goal:
    """ gets string representation of current goal
    """
    pass
