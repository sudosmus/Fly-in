from enum import Enum

class ZoneType(Enum):

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

class Zone:
    
    def __init__(self, name: str, x: int, y: int, 
                zone_type: ZoneType = ZoneType.NORMAL, color: str | None = None, 
                max_drones: int = 1) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones


    def move_cost(self) -> int:
        "Turns needed to enter the zone (default 1, restricted 2)"
        if self.zone_type == ZoneType.BLOCKED:
            raise ValueError(f"Cannot enter the blocked zone {self.name}")
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1
        


class Connection:
    def __init__(self, a: Zone, b: Zone, max_link_capacity: int = 1) -> None:
        self.a = a
        self.b = b
        self.max_link_capacity = max_link_capacity
    
    def other_side(self, zone: Zone) -> Zone:
        if zone is self.a:
            return self.b
        if zone is self.b:
            return self.a
        raise ValueError(f"{zone.name} is not connected here")

class Network:
    def __init__(self, nb_drones: int, zones: dict[str, Zone],
                connections: list[Connection],
                start: Zone,
                end: Zone) -> None:
            self.nb_drones = nb_drones
            self.zones = zones
            self.start = start
            self.end = end
            self.connecteds: dict[str, list[Connection]] = {}
            for name in zones:
                """Loop creates one empty list per zone, zone names as the keys"""
                self.connecteds[name] = []
            for con in connections:
                """Each connection goes into the lists of both zones"""
                self.connecteds[con.a.name].append(con)
                self.connecteds[con.b.name].append(con)
            
