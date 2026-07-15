"""Non-interactive path simulation helper."""

from core.drone import Drone
from core.graph import Graph


class Simulation:
    """Replays a single drone's precomputed path move by move.

    Unlike :class:`simulation.scheduler.Scheduler`, this class does not
    account for capacity constraints or turn-based waiting; it simply
    walks a single drone along its full path in one go.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the simulation for a given graph.

        Args:
            graph: The graph the drone moves through.
        """
        self.graph = graph

    def simulate(
            self,
            drone: Drone,
            path: list[str]
            ) -> list[str]:
        """Move a drone through every zone of its path.

        Args:
            drone: The drone to move. Its ``current_zone`` is updated to
                the last zone in ``path``.
            path: Ordered list of zone names to traverse, starting with
                the drone's current zone.

        Returns:
            The list of move descriptions, formatted as
            ``"D{drone_id}-{zone_name}"``, one per zone visited after the
            first.
        """
        moves = []
        for zone_name in path[1:]:
            moves.append(
                f"D{drone.drone_id}-{zone_name}")

            drone.current_zone = zone_name
        return moves
