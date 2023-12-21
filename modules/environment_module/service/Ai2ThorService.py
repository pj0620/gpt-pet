from ai2thor.controller import Controller

from constants.ai2thor_constants import AI2THOR_ROTATE_LEFT, AI2THOR_NOP
from constants.endpoint_constants import DIR_TO_AI2THOR_MOVEMENT


class Ai2ThorService:
    def __init__(self):
        self.controller = Controller(
            scene="FloorPlan209",
            gridSize=0.25,
            rotateStepDegrees=90,
            # camera properties
            width=1200,
            height=1200,
            fieldOfView=90
        )
        self.controller.step(action="Crouch")
        self.last_event = None

    def move(self, direction: str):
        return self.do_step(DIR_TO_AI2THOR_MOVEMENT[direction])

    def turn(self, degrees: int):
        return self.do_step(AI2THOR_ROTATE_LEFT, degrees=degrees)

    def get_last_image_np(self):
        if self.last_event is None:
            self.do_step(AI2THOR_NOP)
        return self.last_event.frame

    def do_step(self, step: str, **kwargs):
        self.last_event = self.controller.step(step, **kwargs)
        return self.last_event.metadata["lastActionSuccess"]
