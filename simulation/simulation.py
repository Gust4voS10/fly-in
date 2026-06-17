from core.drone import Drone
from core.graph import Graph


class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def simulate(
            self,
            drone: Drone,
            path: list[str]
            ) -> list[str]:
        moves = []
        for zone_name in path[1:]:
            moves.append(
                f"D{drone.drone_id}-{zone_name}")

            drone.current_zone = zone_name
        return moves
