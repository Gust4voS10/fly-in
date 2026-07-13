from core.drone import Drone
from core.graph import Graph
from core.zone import Zone
from core.connection import Connection
from simulation.scheduler import Scheduler


def test_restricted_zone_sets_visual_midpoint_target_and_wait_turn():
    graph = Graph()
    graph.add_zone(Zone("A", 0, 0))
    graph.add_zone(Zone("B", 10, 10, zone_type="restricted"))
    graph.add_connection(Connection("A", "B"))
    graph.start_zone = "A"
    graph.end_zone = "B"

    scheduler = Scheduler(graph)
    drone = Drone(drone_id=1, current_zone="A")
    drone.target_x = 0
    drone.target_y = 0

    scheduler._move_drone(drone, "B", {"A": 1})
    scheduler._process_restricted(drone, "B")

    assert drone.current_zone == "B"
    assert drone.target_x == 5.0
    assert drone.target_y == 5.0
    assert drone.remaining_turns == 1
