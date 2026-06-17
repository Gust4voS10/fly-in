from core.drone import Drone
from core.graph import Graph


class Scheduler:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def execute_turn(
        self,
        drones: list[Drone],
        paths: dict[int, list[str]]
    ) -> list[str]:

        moves: list[str] = []

        occupied = self._get_occupied_zones(drones)

        link_usage: dict[tuple[str, str], int] = {}

        for drone in drones:

            if drone.delivered:
                continue

            if self._process_waiting_drone(drone):
                continue

            move = self._try_move_drone(
                drone,
                paths[drone.drone_id],
                occupied,
                link_usage
            )

            if move is not None:
                moves.append(move)

        return moves

    def _get_occupied_zones(
        self,
        drones: list[Drone]
    ) -> dict[str, int]:

        occupied: dict[str, int] = {}

        for drone in drones:

            if drone.delivered:
                continue

            zone_name = drone.current_zone

            occupied[zone_name] = (
                occupied.get(zone_name, 0) + 1
            )

        return occupied

    def _process_waiting_drone(
        self,
        drone: Drone
    ) -> bool:

        if drone.remaining_turns > 0:

            drone.remaining_turns -= 1

            return True

        return False

    def _get_next_zone(
        self,
        drone: Drone,
        path: list[str]
    ) -> str | None:

        if drone.path_index >= len(path) - 1:
            return None

        return path[drone.path_index + 1]

    def _is_zone_available(
        self,
        zone_name: str,
        occupied: dict[str, int]
    ) -> bool:

        zone = self.graph.zones[zone_name]

        current = occupied.get(zone_name, 0)

        return current < zone.max_drones

    def _find_connection(
        self,
        from_zone: str,
        to_zone: str
    ):

        for connection in self.graph.connections:

            direct = (
                connection.zone1 == from_zone
                and connection.zone2 == to_zone
            )

            reverse = (
                connection.zone1 == from_zone
                and connection.zone2 == to_zone
            )

            if direct or reverse:
                return connection

        return None

    def _is_link_available(
        self,
        from_zone: str,
        to_zone: str,
        link_usage: dict[tuple[str, str], int]
    ) -> bool:

        connection = self._find_connection(
            from_zone,
            to_zone
        )

        if connection is None:
            return False

        key = tuple(
            sorted([from_zone, to_zone])
        )

        current_usage = link_usage.get(
            key,
            0
        )

        return (
            current_usage
            < connection.max_link_capacity
        )

    def _register_link_usage(
        self,
        from_zone: str,
        to_zone: str,
        link_usage: dict[tuple[str, str], int]
    ) -> None:

        key = tuple(
            sorted([from_zone, to_zone])
        )

        link_usage[key] = (
            link_usage.get(key, 0) + 1
        )

    def _move_drone(
        self,
        drone: Drone,
        next_zone: str,
        occupied: dict[str, int]
    ) -> None:

        old_zone = drone.current_zone

        occupied[old_zone] -= 1

        if occupied[old_zone] == 0:
            del occupied[old_zone]

        occupied[next_zone] = (
            occupied.get(next_zone, 0) + 1
        )
        drone.current_zone = next_zone
        drone.path_index += 1

        zone = self.graph.zones[next_zone]
        drone.target_x = zone.x
        drone.target_y = zone.y

    def _process_restricted(
        self,
        drone: Drone,
        zone_name: str
    ) -> None:

        zone = self.graph.zones[zone_name]

        if zone.zone_type == "restricted":
            drone.remaining_turns = 1

    def _check_delivery(
        self,
        drone: Drone,
        path: list[str]
    ) -> None:

        if drone.path_index >= len(path) - 1:
            drone.delivered = True

    def _try_move_drone(
        self,
        drone: Drone,
        path: list[str],
        occupied: dict[str, int],
        link_usage: dict[tuple[str, str], int]
    ) -> str | None:

        next_zone = self._get_next_zone(
            drone,
            path
        )

        if next_zone is None:

            drone.delivered = True

            return None

        if not self._is_zone_available(
            next_zone,
            occupied
        ):
            return None

        if not self._is_link_available(
            drone.current_zone,
            next_zone,
            link_usage
        ):
            return None

        self._register_link_usage(
            drone.current_zone,
            next_zone,
            link_usage
        )

        self._move_drone(
            drone,
            next_zone,
            occupied
        )

        self._process_restricted(
            drone,
            next_zone
        )

        self._check_delivery(
            drone,
            path
        )

        return (
            f"D{drone.drone_id}-{next_zone}"
        )
