import sys

from parser import MapParser, ParseError
from path_finder import Pathfinder

def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    try:
        network = MapParser().parse(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: file not found: {sys.argv[1]}")
        sys.exit(1)
    except ParseError as error:
        print(f"Error: {error}")
        sys.exit(1)
    
    print(f"{network.nb_drones} drones")
    print(f"start: {network.start.name}, end: {network.end.name}")
    for name, zone in network.zones.items():
        print(f"{name} ({zone.x}, {zone.y}) {zone.zone_type.value} "
            f"max_drones= {zone.max_drones} color= {zone.color}")
    for name, con in network.connecteds.items():
        current_zone = network.zones[name]
        neighbors = [c.other_side(current_zone).name for c in con]
        print(f" {name} connects to: {neighbors}")

    distances = Pathfinder(network).distance_to_goal()
    if network.start.name not in distances:
        print("Error: no path found")
        sys.exit(1)
    for name, dist in distances.items():
        print(f"{name}: {dist}")
    

if __name__ == "__main__":
    main()