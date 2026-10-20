import sys

from parser import MapParser, ParseError

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
        neighbors = []
        for c in con:
            current_zone = network.zones[name]
            other_zone = c.other_side(current_zone)
            neighbors.append(other_zone.name)
        print(f" {current_zone.name} connects to: {neighbors}")

if __name__ == "__main__":
    main()