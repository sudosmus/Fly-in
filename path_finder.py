from models import Network, ZoneType
import heapq

class Pathfinder():
    def __init__(self, network: Network) -> None:
        self.network = network
        
    def distance_to_goal(self) -> dict[str, int]:
        end = self.network.end
        
        best_cost: dict[str, int] = {end.name: 0}
        queue: list[tuple[int, str]] = [(0, end.name)]
        
        while queue:
            cost, name = heapq.heappop(queue)
            
            """best cost for the zone stays the same"""
            if cost > best_cost[name]:
                continue
            
            zone = self.network.zones[name]
            for con in self.network.connecteds[name]:
                neighbor = con.other_side(zone)
                
                if neighbor.zone_type == ZoneType.BLOCKED:
                    continue
                
                new_cost = cost + zone.move_cost()
                old_cost = best_cost.get(neighbor.name)
                
                if old_cost is None or new_cost < old_cost:
                    best_cost[neighbor.name] = new_cost
                    heapq.heappush(queue, (new_cost, neighbor.name))
                    
        return best_cost
        