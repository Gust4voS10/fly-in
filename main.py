from algorithms.dijkstra import Dijkstra
from core.drone import Drone
from parser.parser import Parser
from simulation.scheduler import Scheduler


def main() -> None:

    parser = Parser("test.txt")

    graph = parser.parse()

    dijkstra = Dijkstra(graph)

    drones: list[Drone] = []

    paths: dict[int, list[str]] = {}

    for drone_id in range(1, parser.nb_drones + 1):

        drone = Drone(
            drone_id=drone_id,
            current_zone=graph.start_zone
        )

        drones.append(drone)
        path = dijkstra.find_path(
            graph.start_zone,
            graph.end_zone
        )

        if not path:
            raise ValueError(
                f"No path found for drone {drone_id}"
            )

        paths[drone_id] = path

    print("\nPaths encontrados:")
    print(
        f"Drone {drone_id}: "
        f"{' -> '.join(path)}"
    )

    scheduler = Scheduler(graph)

    turn = 1

    while not all(
        drone.delivered
        for drone in drones
    ):

        moves = scheduler.execute_turn(
            drones,
            paths
        )

        print(
            f"\nTurn {turn}: "
            + (
                " ".join(moves)
                if moves
                else "(no moves)"
            )
        )

        turn += 1

    print("\nSimulation complete!")


if __name__ == "__main__":
    main()