from algorithms.dijkstra import Dijkstra
from core.drone import Drone
from parser.parser import Parser
from simulation.scheduler import Scheduler
from visualization.renderer import Renderer


def main() -> None:

    parser = Parser("test.txt")

    graph = parser.parse()

    dijkstra = Dijkstra(graph)

    drones: list[Drone] = []
    paths: dict[int, list[str]] = {}

    predicted_usage: dict[str, int] = {}

    for drone_id in range(
        1,
        parser.nb_drones + 1
    ):
        path = dijkstra.find_path(
            graph.start_zone,
            graph.end_zone,
            predicted_usage
        )

        if not path:
            raise ValueError("No path found from start to goal")

        drone = Drone(
            drone_id=drone_id,
            current_zone=graph.start_zone
        )

        start_zone = graph.zones[graph.start_zone]
        drone.visual_x = start_zone.x
        drone.visual_y = start_zone.y
        drone.target_x = start_zone.x
        drone.target_y = start_zone.y

        drones.append(drone)

        paths[drone_id] = path

        for zone in path:
            predicted_usage[zone] = (
                predicted_usage.get(zone, 0) + 1
            )

    scheduler = Scheduler(graph)

    renderer = Renderer(
        graph,
        drones
    )
    renderer.run(scheduler, paths)


if __name__ == "__main__":
    main()
