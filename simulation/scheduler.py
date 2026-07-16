"""Turn-based, capacity-aware drone scheduler.

This module executes the fleet simulation one discrete turn at a time,
enforcing zone capacity (``max_drones``) and link capacity
(``max_link_capacity``) constraints, handling waiting/queuing at
bottlenecks, and pausing drones for one extra turn when they enter
``restricted`` zones.
"""

from core.connection import Connection
from core.drone import Drone
from core.graph import Graph


class Scheduler:
    """Advances every drone in the fleet by one simulation turn at a time."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the scheduler for a given graph.

        Args:
            graph: The graph drones move through.
        """
        self.graph = graph

    def execute_turn(
        self,
        drones: list[Drone],
        paths: dict[int, list[str]]
    ) -> list[str]:
        """Advance every non-delivered drone by (at most) one hop.

        For each drone still in transit, this either counts down a
        waiting timer (see :meth:`_process_waiting_drone`) or attempts to
        move it to the next zone in its path (see
        :meth:`_try_move_drone`), respecting current zone/link occupancy.

        Args:
            drones: All drones in the fleet.
            paths: Mapping of drone ID to its precomputed path (ordered
                list of zone names).

        Returns:
            The list of move descriptions produced this turn, formatted
            as ``"D{drone_id}-{zone_name}"``.
        """

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
        """Count how many non-delivered drones currently occupy each zone.

        Args:
            drones: All drones in the fleet.

        Returns:
            Mapping of zone name to the number of drones currently in it.
        """

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
        """Advance a drone's waiting timer, if it has one.

        Args:
            drone: The drone to process.

        Returns:
            ``True`` if the drone was waiting this turn (and therefore
            should not attempt to move), ``False`` otherwise. When the
            waiting timer reaches zero, the drone's visual target is reset
            to its current zone's coordinates.
        """

        if drone.remaining_turns > 0:

            drone.remaining_turns -= 1

            if drone.remaining_turns == 0:
                self._set_visual_target_to_current_zone(drone)

            return True

        return False

    def _get_next_zone(
        self,
        drone: Drone,
        path: list[str]
    ) -> str | None:
        """Return the next zone a drone should move toward.

        Args:
            drone: The drone whose path is being followed.
            path: The drone's precomputed path.

        Returns:
            The name of the next zone in ``path`` (forward or backward
            depending on ``drone.reverse_mode``), or ``None`` if the drone
            has already reached the end of its path in the current
            direction.
        """

        if not drone.reverse_mode:
            if drone.path_index >= len(path) - 1:
                return None

            return path[drone.path_index + 1]

        if drone.path_index <= 0:
            return None

        return path[drone.path_index - 1]

    def _is_zone_available(
        self,
        zone_name: str,
        occupied: dict[str, int]
    ) -> bool:
        """Check whether a zone has spare capacity for one more drone.

        Args:
            zone_name: Name of the zone to check.
            occupied: Mapping of zone name to current occupancy, as
                returned by :meth:`_get_occupied_zones`.

        Returns:
            ``True`` if the zone's current occupancy is below its
            ``max_drones`` limit.
        """

        zone = self.graph.zones[zone_name]

        current = occupied.get(zone_name, 0)

        return current < zone.max_drones

    def _find_connection(
        self,
        from_zone: str,
        to_zone: str
    ) -> Connection | None:
        """Find the connection object linking two zones, if any.

        Args:
            from_zone: Name of one endpoint zone.
            to_zone: Name of the other endpoint zone.

        Returns:
            The matching :class:`core.connection.Connection` (checked in
            both directions), or ``None`` if no such connection exists.
        """

        for connection in self.graph.connections:

            direct = (
                connection.zone1 == from_zone
                and connection.zone2 == to_zone
            )

            reverse = (
                connection.zone1 == to_zone
                and connection.zone2 == from_zone
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
        """Check whether a link still has spare capacity this turn.

        Args:
            from_zone: Name of the zone being left.
            to_zone: Name of the zone being entered.
            link_usage: Mapping of (sorted) zone-name pairs to how many
                drones have already crossed that link this turn.

        Returns:
            ``True`` if a connection exists between the two zones and its
            usage this turn is below ``max_link_capacity``, ``False``
            otherwise (including when no connection exists).
        """

        connection = self._find_connection(
            from_zone,
            to_zone
        )

        if connection is None:
            return False

        key = (
            (from_zone, to_zone)
            if from_zone <= to_zone
            else (to_zone, from_zone)
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
        """Record that a drone has crossed a link this turn.

        Args:
            from_zone: Name of the zone left.
            to_zone: Name of the zone entered.
            link_usage: Mapping of (sorted) zone-name pairs to crossing
                count this turn, updated in place.
        """

        key = (
            (from_zone, to_zone)
            if from_zone <= to_zone
            else (to_zone, from_zone)
        )

        link_usage[key] = (
            link_usage.get(key, 0) + 1
        )

    def _set_visual_target_to_current_zone(
        self,
        drone: Drone
    ) -> None:
        """Point a drone's visual animation target at its current zone.

        Args:
            drone: The drone whose visual target should be updated.
        """

        zone = self.graph.zones[drone.current_zone]
        drone.target_x = zone.x
        drone.target_y = zone.y

    def _set_visual_target_to_midpoint(
        self,
        drone: Drone,
        from_zone: str,
        to_zone: str
    ) -> None:
        """Point a drone's visual animation target at a link's midpoint.

        Used when a drone enters a ``restricted`` zone, so it visibly
        pauses partway along the link while it waits out the extra turn.

        Args:
            drone: The drone whose visual target should be updated.
            from_zone: Name of the zone the drone came from.
            to_zone: Name of the zone the drone is entering.
        """

        from_zone_data = self.graph.zones[from_zone]
        to_zone_data = self.graph.zones[to_zone]

        drone.target_x = (
            from_zone_data.x + to_zone_data.x
        ) / 2
        drone.target_y = (
            from_zone_data.y + to_zone_data.y
        ) / 2

    def _move_drone(
        self,
        drone: Drone,
        next_zone: str,
        occupied: dict[str, int]
    ) -> None:
        """Move a drone into a new zone and update its bookkeeping.

        Updates ``occupied`` in place, moves ``drone.current_zone``,
        advances or rewinds ``drone.path_index`` depending on
        ``reverse_mode``, and sets the drone's visual animation target
        (using the link midpoint if the destination is ``restricted``).

        Args:
            drone: The drone being moved.
            next_zone: Name of the zone the drone is moving into.
            occupied: Mapping of zone name to current occupancy, updated
                in place.
        """

        old_zone = drone.current_zone

        occupied[old_zone] -= 1

        if occupied[old_zone] == 0:
            del occupied[old_zone]

        occupied[next_zone] = (
            occupied.get(next_zone, 0) + 1
        )
        drone.current_zone = next_zone
        if drone.reverse_mode:
            drone.path_index -= 1
        else:
            drone.path_index += 1

        zone = self.graph.zones[next_zone]
        if zone.zone_type == "restricted":
            self._set_visual_target_to_midpoint(
                drone,
                old_zone,
                next_zone
            )
        else:
            drone.target_x = zone.x
            drone.target_y = zone.y

    def _process_restricted(
        self,
        drone: Drone,
        zone_name: str
    ) -> None:
        """Make a drone wait one extra turn if it entered a restricted zone.

        Args:
            drone: The drone that just moved.
            zone_name: Name of the zone the drone just entered.
        """

        zone = self.graph.zones[zone_name]

        if zone.zone_type == "restricted":
            drone.remaining_turns = 1

    def _check_delivery(
        self,
        drone: Drone,
        path: list[str]
    ) -> None:
        """Mark a drone as delivered once it reaches the end of its path.

        In forward mode, delivery happens at the last index of ``path``.
        In reverse mode, delivery happens back at index 0.

        Args:
            drone: The drone to check.
            path: The drone's precomputed path.
        """

        if not drone.reverse_mode:
            if drone.path_index >= len(path) - 1:
                drone.delivered = True
                drone.reverse_mode = False
            return

        if drone.path_index <= 0:
            drone.delivered = True
            drone.reverse_mode = False

    def _try_move_drone(
        self,
        drone: Drone,
        path: list[str],
        occupied: dict[str, int],
        link_usage: dict[tuple[str, str], int]
    ) -> str | None:
        """Attempt to advance a single drone by one hop this turn.

        Checks the next zone in the drone's path, verifies both zone and
        link capacity are available, and if so performs the move,
        applies the restricted-zone wait rule, and checks for delivery.

        Args:
            drone: The drone to attempt to move.
            path: The drone's precomputed path.
            occupied: Mapping of zone name to current occupancy, updated
                in place if the move succeeds.
            link_usage: Mapping of (sorted) zone-name pairs to crossing
                count this turn, updated in place if the move succeeds.

        Returns:
            A move description formatted as ``"D{drone_id}-{zone_name}"``
            if the drone moved this turn, or ``None`` if it has completed
            its path (marked as delivered) or could not move due to
            capacity constraints.
        """

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
