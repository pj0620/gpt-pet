from gptpet_context import GPTPetContext
from model.passageway import Passageway, PhysicalPassagewayInfo, PassagewayDescription


def merge_passageways(
  context: GPTPetContext,
  passageway_descriptions: list[PassagewayDescription],
  physical_passageways: list[PhysicalPassagewayInfo]
) -> list[Passageway]:
  color_to_physical = {
    physical_passageway.color: physical_passageway
    for physical_passageway in physical_passageways
  }
  passageways = []
  for passageway_description in passageway_descriptions:
    if passageway_description.color in color_to_physical:
      passageways.append(Passageway(
        color=passageway_description.color,
        description=passageway_description.description,
        name=passageway_description.name,
        turn_degrees=color_to_physical[passageway_description.color].turn_degrees
      ))
    else:
      context.analytics_service.new_text(f"Vision LLM detected an invalid passageway: {passageway_description}")
  return passageways
