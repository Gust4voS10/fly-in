"""Entry point: pick a map, compute drone paths, and run the simulation.

Lists every ``.txt`` map found under ``maps/`` (plus ``test.txt`` at the
repository root if present), lets the user pick one interactively, parses
it into a graph, computes a Dijkstra path for every drone (updating a
predicted-usage map incrementally to spread the fleet across alternative
routes), and finally launches the ``pygame`` renderer to simulate and
visualize the fleet's movement.
"""

from algorithms.dijkstra import Dijkstra
from core.drone import Drone
from parser.parser import Parser
from simulation.scheduler import Scheduler
from visualization.renderer import Renderer
from pathlib import Path


def select_map() -> str:
    """Interactively prompt the user to choose a map file.

    Scans ``maps/`` recursively for ``.txt`` files (sorted alphabetically)
    and includes ``test.txt`` from the repository root first, if present.
    Prints the list and repeatedly prompts until a valid choice is made.

    Returns:
        The path of the selected map file. Falls back to ``"test.txt"``
        if no map files are found at all.
    """
    maps_dir = Path("maps")
    map_files = []

    if maps_dir.exists():
        for txt_file in sorted(maps_dir.rglob("*.txt")):
            map_files.append(str(txt_file))

    if Path("test.txt").exists():
        map_files.insert(0, "test.txt")

    if not map_files:
        print("Nenhum mapa encontrado!")
        return "test.txt"

    print("\n=== MAPAS DISPONÍVEIS ===\n")
    for idx, map_file in enumerate(map_files, 1):
        print(f"{idx}. {map_file}")

    while True:
        try:
            choice = input("\nEscolha um mapa (número): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(map_files):
                selected = map_files[choice_num - 1]
                print(f"\nMapa selecionado: {selected}\n")
                return selected
            else:
                print(f"Por favor, escolha um "
                      f"número entre 1 e {len(map_files)}")
        except ValueError:
            print("Entrada inválida! Digite um número.")


def main() -> None:
    """Parse a map, compute paths for every drone, and run the simulation.

    Raises:
        ValueError: If no valid path can be found from the start zone to
            the end zone for any drone.
    """

    map_file = select_map()
    parser = Parser(map_file)

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
