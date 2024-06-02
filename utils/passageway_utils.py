from model.passageway import Passageway, PhysicalPassagewayInfo, PassagewayDescription


def merge_passageways(
  passageway_descriptions: list[PassagewayDescription],
  physical_passageways: list[PhysicalPassagewayInfo]
) -> list[Passageway]:
  color_to_physical = {
    physical_passageway.color: physical_passageway
    for physical_passageway in physical_passageways
  }
  passageways = [
    Passageway(
      color=passageway_description.color,
      description=passageway_description.description,
      name=passageway_description.name,
      turn_degrees=color_to_physical[passageway_description.color].turn_degrees
    )
    for passageway_description in passageway_descriptions
  ]
  return passageways
