from models import Zone, Connection, Network, ZoneType
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
        
class ReservationTable():
    def __init__(self, network: Network) -> None:
        self.network = network
        
        """(turn, zone name) -> number of drones in that zone"""
        self.zone_usage: dict[tuple[int, str], int] = {}
        
        """(turn, pair of zone names) -> drones using that connection"""
        self.connection_usage: dict[tuple[int, frozenset[str]], int]
        
    def zone_free(self, zone: Zone, turn: int) -> bool:
        """checks if there's free space in a zone"""
        if zone is self.network.start or zone is self.network.end:
            return True
        used = self.zone_usage.get((turn, zone.name), 0)
        return used < zone.max_drones
        
    def link_free(self, link: Connection, turn: int) -> bool:
        """checks if there is free space in a connection"""
        used = self.connection_usage.get((turn, frozenset({link.a.name, link.b.name}), 0))
        return used < link.max_link_capacity
    
    def reserve_zone(self, zone: Zone, turn: int) -> None:
        """books one place in this zone at this turn"""
        key = (turn, zone.name)
        self.zone_usage[key] = self.zone_usage.get(key, 0) + 1
        
    def reserve_link(self, link: Connection, turn: int) -> None:
        """books a spot in the link on this turn"""
        key = (turn, frozenset({link.a.name, link.b.name}))
        self.connection_usage[key] = self.connection_usage.get(key, 0) + 1
        

""" where is the drone in this turn"""
State = tuple[int, str]
""" state plus how it came there"""
Step = tuple[int, str, Connection | None]

class Scheduler:
    def __init__(self, network: Network) -> None:
        self.network = network
        self.table = ReservationTable(network)
    
    def find_route(self)





