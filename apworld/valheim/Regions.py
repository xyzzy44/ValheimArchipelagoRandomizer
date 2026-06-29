from typing import Dict, List, NamedTuple, Callable, TYPE_CHECKING
from BaseClasses import Region, Entrance, CollectionState

if TYPE_CHECKING:
    from . import ValheimWorld


class ValheimConnection(NamedTuple):
    destination: str  # Name of the region the connection leads to
    required_items: Dict[str, int]  # Item name → Count required


class ValheimRegion(NamedTuple):
    connections: List[ValheimConnection]  # List of connections from this region


def create_connection_rule(required_items: Dict[str, int], world: "ValheimWorld", destregion) -> Callable[[CollectionState], bool]:
    """
    Generate an access rule for a connection based on required items.
    """
    match destregion:
        case "Tier1":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has("Leather Armor", world.player) and state.has("Bows Tier 1", world.player) and state.has_any(["Axes Tier 1","Spears Tier 1"], world.player) 
        case "Tier3":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has_any(["Troll Armor","Bear Armor","Bronze Armor"], world.player) and state.has("Bows Tier 2", world.player) and state.has_any(["Axes Tier 2","Sledgehammers Tier 1","Clubs Tier 2","Blades Tier 2","Spears Tier 2","Polearms Tier 1"], world.player)
        case "Tier4":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has_any(["Root Armor","Iron Armor"], world.player) and state.has("Bows Tier 3", world.player) and state.has_any(["Axes Tier 3","Sledgehammers Tier 2","Clubs Tier 3","Blades Tier 3","Spears Tier 3","Polearms Tier 2","Battleaxes Tier 1"], world.player)
        case "Tier7":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has_any(["Fenris Armor","Wolf Armor"], world.player) and state.has("Bows Tier 4", world.player) and state.has_any(["Clubs Tier 4","Blades Tier 4","Spears Tier 4","Battleaxes Tier 2"], world.player)
        case "Tier8":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has_any(["Vilebone Armor","Padded Armor"], world.player) and state.has_any(["Clubs Tier 5","Blades Tier 5","Battleaxes Tier 3","Polearms Tier 3"], world.player)
        case "Tier10":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has("Carapace Armor", world.player) and state.has("Bows Tier 5", world.player) and state.has_any(["Spears Tier 5","Blades Tier 6","Battleaxes Tier 4","Polearms Tier 4"], world.player)
        case "Tier11":
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player) and state.has_any(["Flametal Armor","Ask Armor"], world.player) and state.has("Bows Tier 6", world.player) and state.has_any(["Blades Tier 7","Battleaxes Tier 5","Spears Tier 6"], world.player)
        case _:
            def rule(state: CollectionState) -> bool:
                return state.has_all_counts(required_items, world.player)
    return rule


# Define regions and their connections parsed from a text file
region_data_table: Dict[str, ValheimRegion] = {}

# Example region connections text data
region_txt = '''
Menu,Tier0
Tier0,Tier1,Crafting,1
Tier1,Tier2,Axes Tier 1,1,Bed Tier 1,1,Cooking Station,1,Troll Armor,1,Warmth Tier 1,1,Wooden Beams,1,Wooden Roofs,1,Wooden Floors,1
Tier2,Tier3,Boat Tier 1,1,Forge,1,Pickaxes Tier 1,1,Smelter,1,Charcoal Kiln,1
Tier3,Tier4,Bronze,1
Tier4,Tier5,Axes Tier 2,1,Iron Cooking Station,1,Cauldron,1
Tier5,Tier6,Pickaxes Tier 2,1
Tier6,Tier7,Forge Upgrade 1,1,Nails Tier 2,1,Pickaxes Tier 3,1
Tier7,Tier8,Artisan Table,1,Blast Furnace,1
Tier8,Tier9,Axes Tier 4,1,Forge Upgrade 2,1,Forge Upgrade 3,1,Spinning Wheel,1,Wisp Fountain,1,Wisplight,1
Tier9,Tier10,Pickaxes Tier 4,1
Tier10,Tier11,Artisan Press,1,Boat Tier 4,1,Ceramic Plates,1
'''

# Parse region data
for line in region_txt.strip().splitlines():
    if not line or line.startswith("//"):
        continue

    parts = line.split(",")
    if len(parts) < 2:
        print(f"Malformed line: {line}")  # Debugging output
        continue

    source_region = parts[0].strip()
    destination_region = parts[1].strip()
    required_items = {}

    # Parse item requirements if available
    if len(parts) > 2:
        for i in range(2, len(parts), 2):
            item = parts[i].strip()
            count = int(parts[i + 1].strip())
            required_items[item] = count

    # Ensure the source region exists
    if source_region not in region_data_table:
        region_data_table[source_region] = ValheimRegion(connections=[])

    # Add the connection to the source region
    region_data_table[source_region].connections.append(
        ValheimConnection(destination=destination_region, required_items=required_items)
    )

    # Ensure the destination region exists (even if it has no connections initially)
    if destination_region not in region_data_table:
        region_data_table[destination_region] = ValheimRegion(connections=[])


def create_regions(world: "ValheimWorld"):
    """
    Step 1: Create all regions and add them to the multiworld.
    """
    created_regions = {
        region_name: Region(region_name, world.player, world.multiworld)
        for region_name in region_data_table
    }
    world.multiworld.regions.extend(created_regions.values())

    """
    Step 2: Add connections between regions using entrances.
    """
    for region_name, region in region_data_table.items():
        source_region = created_regions[region_name]

        for connection in region.connections:
            destination_region = created_regions[connection.destination]

            # Create an entrance in the source region leading to the destination
            entrance_name = f"{source_region.name} -> {destination_region.name}"
            entrance = Entrance(world.player, entrance_name, source_region)

            # Connect the entrance to the destination region
            entrance.connect(destination_region)

            # If the connection has access rules, assign them to the entrance
            if connection.required_items:
                entrance.access_rule = create_connection_rule(connection.required_items, world, destination_region.name)

            # Add the entrance to the source region's exits
            source_region.exits.append(entrance)
