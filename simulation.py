from models import Zone, Connection, Network, ZoneType
from path_finder import Pathfinder

class Drone:
    
    def __init__(self, drone_id: int, zone: Zone) -> None:
        self.drone_id = drone_id
        self.zone = zone
        self.flying_to: Zone | None = None
        self.delivered = False


class Simulation:

    def __init__(self, network: Network) -> None:
        self.network = network
        self.distances = Pathfinder(network).distance_to_goal()
        self.drones = [Drone(i, network.start)
                        for i in range(1, network.nb_drones + 1)]
        self.occupancy: dict[str, int] = {name: 0 for name in network.zones}
        self.occupancy[network.start.name] = network.nb_drones

    def run(self) -> list[str]:
        lines: list[str] = []
        while not all(drone.delivered for drone in self.drones):
            moves = self._play_turn()
            if not moves:
                raise RuntimeError("drones cannot move")
            lines.append(" ".join(moves))
        return lines

    def _play_turn(self) -> list[str]:
        moves: list[str] = []
        link_used: dict[frozenset[str], int] = {}
        landed: set[int] = set()

        #flying drones land
        for drone in self.drones:
            if drone.flying_to is not None:
                drone.zone = drone.flying_to
                drone.flying_to = None
                landed.add(drone.drone_id)
                moves.append(f"D{drone.drone_id}-{drone.zone.name}")
                if drone.zone is self.network.end:
                    drone.delivered = True

        #drones on the ground, closest to the end first
        ground = [d for d in self.drones
                    if not d.delivered and d.flying_to is None
                    and d.drone_id not in landed]
        ground.sort(key=lambda d: (self.distances[d.zone.name], d.drone_id))

        #each drone moves if it can, otherwise waits
        for drone in ground:
            choice = self._choose_next(drone, link_used)
            if choice is None:
                continue
            target, link = choice
            self.occupancy[drone.zone.name] -= 1
            self.occupancy[target.name] += 1
            key = frozenset({link.a.name, link.b.name})
            link_used[key] = link_used.get(key, 0) + 1

            if target.zone_type == ZoneType.RESTRICTED:
                drone.flying_to = target
                moves.append(f"D{drone.drone_id}-{link.a.name}-{link.b.name}")
            else:
                drone.zone = target
                moves.append(f"D{drone.drone_id}-{target.name}")
                if target is self.network.end:
                    drone.delivered = True
        return moves

    def _choose_next(self, drone: Drone, link_used: dict[frozenset[str], int]
                    ) -> tuple[Zone, Connection] | None:
        """Pick the best free neighbor closer to the end or None to wait"""
        here = self.distances[drone.zone.name]
        options: list[tuple[int, int, str, Zone, Connection]] = []
        for link in self.network.connecteds[drone.zone.name]:
            neighbor = link.other_side(drone.zone)
            if neighbor.zone_type == ZoneType.BLOCKED:
                continue
            if neighbor.name not in self.distances:
                continue
            if self.distances[neighbor.name] >= here:
                continue
            total = neighbor.move_cost() + self.distances[neighbor.name]
            not_priority = 0 if neighbor.zone_type == ZoneType.PRIORITY else 1
            options.append((total, not_priority, neighbor.name, neighbor, link))

        for _, _, _, neighbor, link in sorted(options):
            key = frozenset({link.a.name, link.b.name})
            if link_used.get(key, 0) >= link.max_link_capacity:
                continue
            if neighbor.zone_type == ZoneType.RESTRICTED:
                if not self._has_room_on_landing(neighbor):
                    continue
            elif not self._has_room(neighbor):
                continue
            return neighbor, link
        return None

    def _has_room(self, zone: Zone) -> bool:
        if zone is self.network.start or zone is self.network.end:
            return True
        return self.occupancy[zone.name] < zone.max_drones

    def _has_room_on_landing(self, zone: Zone) -> bool:
        """Check if the drone taking off now can land in zone next turn"""
        if zone is self.network.end:
            return True
        taken = self.occupancy[zone.name] - self._sure_to_leave(zone)
        return taken < zone.max_drones

    def _sure_to_leave(self, zone: Zone) -> int:
        """Count the drones in zone that reach the end next turn"""
        for link in self.network.connecteds[zone.name]:
            if link.other_side(zone) is self.network.end:
                inside = 0
                for drone in self.drones:
                    if (not drone.delivered and drone.flying_to is None
                            and drone.zone is zone):
                        inside += 1
                return min(inside, link.max_link_capacity)
        return 0