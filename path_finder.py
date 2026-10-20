from models import Zone, Connection, Network, ZoneType
import heapq

class Pathfinder():
    def __init__(self, network: Network) -> None:
        self.network = network
    
    def shortest_path(self) -> list[Zone] | None:
        start = self.network.start
        end = self.network.end

        best_cost: dict[str, int] = {start.name: 0}
        came_from: dict[str, str] = {}
        queue: list[tuple[int, str]] = [(0, start.name)]

        while queue:
            cost, name = heapq.heappop(queue)

            if name == end.name:
                return self._build_path(came_from, end.name)
            
            if cost > best_cost[name]:
                continue
            zone = self.network.zones[name]
            for con in self.network.connecteds[name]:
                neighbor = con.other_side(zone)

                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue

                new_cost = cost + neighbor.move_cost()
                old_cost = best_cost.get(neighbor.name)

                if old_cost is None or new_cost < old_cost:
                    best_cost[neighbor.name] = new_cost
                    came_from[neighbor.name] = name
                    heapq.heappush(queue, (new_cost, neighbor.name))
        return None

    
    def _build_path(self, came_from: dict[str, str], end_name: str) -> list[Zone]:
        names: list[Zone] = [end_name]
        while names[-1] in came_from:
            names.append(came_from[names[-1]])
        names.reverse()
        return [self.network.zones[n] for n in names]





