from gptpet_context import GPTPetContext
from mixin.goal.base_goal_mixin import BaseGoalMixin
from model.goal import Goal
from service.analytics_service import AnalyticsService
from service.vectordb_adapter_service import VectorDBAdapterService

DEFAULT_GOAL = "explore your environment"


class SimpleChainGoalMixin(BaseGoalMixin):
  def __init__(
      self,
      analytics_service: AnalyticsService,
      vectordb_adapter: VectorDBAdapterService
  ):
    self.goal = None
    self.analytics_service = analytics_service
    self.vectordb_adapter = vectordb_adapter
    
    self.create_default_goal_if_nonexistant()
  
  def update_goal(self, new_goal: str, last_goal_completed: bool) -> None:
    if self.goal.description == new_goal:
      self.analytics_service.new_text("new goal matches old goal not updating")
      return
    self.analytics_service.new_text(f"setting new goal to: {new_goal}")
    
    # mark goal as completed if applicable
    if last_goal_completed:
      self.analytics_service.new_text(f"setting goal={self.goal} to completed={last_goal_completed}")
      self.vectordb_adapter.set_goal_completed(
        goal_id=self.goal.goal_id,
        goal_completed=last_goal_completed
      )
      
    # create / get new goal
    self.goal = self.vectordb_adapter.get_similar_goal(new_goal)
    if self.goal is None:
      self.analytics_service.new_text(f"found no matching new_goal=`{new_goal}`, creating new goal")
      self.goal = self.vectordb_adapter.create_goal(new_goal)
      self.analytics_service.new_text(f"goal is now: {self.goal}")
      # TODO: how to handle error
    else:
      self.analytics_service.new_text(f"found matching goal for new_goal=`{new_goal}`")
      self.analytics_service.new_text(f"goal is now: {self.goal}")
  
  def get_current_goal(self) -> Goal:
    return self.goal
  
  def create_default_goal_if_nonexistant(self):
    self.analytics_service.new_text(f"checking if default goal already exists: {DEFAULT_GOAL}")
    self.goal = self.vectordb_adapter.get_similar_goal(DEFAULT_GOAL)
    if self.goal is None:
      self.analytics_service.new_text(f"found no matching goal, creating default goal: {DEFAULT_GOAL}")
      self.goal = self.vectordb_adapter.create_goal(DEFAULT_GOAL)
      self.analytics_service.new_text(f"successfully created default goal: {self.goal}")
    else:
      self.analytics_service.new_text(f"found default goal already exists: {self.goal}")
    self.analytics_service.new_text(f"goal is now: {self.goal}")
