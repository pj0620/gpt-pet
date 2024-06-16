from gptpet_context import GPTPetContext
from mixin.goal.base_goal_mixin import BaseGoalMixin
from model.goal import Goal
from service.analytics_service import AnalyticsService


class SimpleChainGoalMixin(BaseGoalMixin):
  def __init__(self, analytics_service: AnalyticsService):
    self.goal = Goal(None, False)
    self.analytics_service = analytics_service
  
  def update_goal(self, new_goal: str) -> None:
    if self.goal.description == new_goal:
      self.analytics_service.new_text("new goal matches old goal not updating")
      return
    else:
      self.analytics_service.new_text(f"setting new goal to: {new_goal}")
      self.goal = Goal(new_goal, False)
  
  def get_current_goal(self) -> Goal:
    return self.goal
