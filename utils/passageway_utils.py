from model.passageway import Passageway, PhysicalPassagewayInfo, PassagewayDescription


def merge_passageways(
  passageway_descriptions: list[PassagewayDescription],
  physical_passageways: list[PhysicalPassagewayInfo]
) -> list[Passageway]:
  color_to_physical = {
    physical_passageway.color : physical_passageway
    for physical_passageway in physical_passageways
  }
  passageways = [
    Passageway(
      physical_passageway=color_to_physical[passageway_description.color],
      passageway_description=passageway_description
    )
    for passageway_description in passageway_descriptions
  ]
  return passageways
