"""Traffic-aware Dijkstra pathfinding.

This module implements a variant of Dijkstra's algorithm whose edge weight
combines the destination zone's traversal cost, a traffic penalty derived
from the fleet's predicted zone usage, and a penalty for low-capacity
connections. This makes the algorithm prefer ``priority`` zones, avoid
``restricted``/congested zones when possible, and naturally spread drones
across alternative routes.
"""

import heapq

from core.graph import Graph


class Dijkstra:
    """Computes shortest, traffic-aware paths over a :class:`Graph`."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the algorithm for a given graph.

        Args:
            graph: The graph to run pathfinding on.
        """
        self.graph = graph

    def _zone_cost(self, zone_name: str) -> float:
        """Return the base traversal cost of entering a zone.

        Args:
            zone_name: Name of the zone being entered.

        Returns:
            ``0.5`` for ``priority`` zones, ``2`` for ``restricted`` zones,
            and ``1`` for any other zone type.
        """

        zone = self.graph.zones[zone_name]

        if zone.zone_type == "priority":
            return 0.5

        if zone.zone_type == "restricted":
            return 2

        return 1

    def _traffic_penalty(
        self,
        zone_name: str,
        predicted_usage: dict[str, int]
    ) -> float:
        """Return an extra cost proportional to a zone's predicted usage.

        Args:
            zone_name: Name of the zone being entered.
            predicted_usage: Mapping of zone name to the number of drones
                already expected to pass through it.

        Returns:
            ``predicted_usage[zone_name] * 2``, or ``0`` if the zone has no
            recorded usage yet.
        """

        return predicted_usage.get(
            zone_name,
            0
        ) * 2

    def _connection_penalty(
            self,
            from_zone: str,
            to_zone: str
            ) -> float:
        """Return an extra cost for crossing a low-capacity connection.

        Args:
            from_zone: Name of the zone being left.
            to_zone: Name of the zone being entered.

        Returns:
            ``1 / max_link_capacity`` of the connection between the two
            zones, or ``0`` if no such connection exists.
        """

        for connection in self.graph.connections:

            if (
                connection.zone1 == from_zone
                and connection.zone2 == to_zone
            ) or (
                connection.zone1 == to_zone
                and connection.zone2 == from_zone
            ):

                return 1 / connection.max_link_capacity

        return 0

    def find_path(
        self,
        start: str,
        end: str,
        predicted_usage: dict[str, int] | None
    ) -> list[str]:
        """Find the lowest-cost path between two zones.

        Runs Dijkstra's algorithm using a combined weight of zone cost,
        traffic penalty, and connection penalty for every edge. ``blocked``
        zones are never expanded into.

        Args:
            start: Name of the starting zone.
            end: Name of the destination zone.
            predicted_usage: Mapping of zone name to the number of drones
                already expected to pass through it, used to penalize
                congested zones. May be ``None``, treated as empty.

        Returns:
            The list of zone names forming the path from ``start`` to
            ``end`` (inclusive), or an empty list if no path exists.
        """

        if predicted_usage is None:
            predicted_usage = {}

        distances: dict[str, float] = {
            zone_name: float("inf")
            for zone_name in self.graph.zones
        }

        previous: dict[str, str | None] = {
            zone_name: None
            for zone_name in self.graph.zones
        }

        distances[start] = 0

        priority_queue: list[tuple[float, str]] = [
            (0, start)
        ]

        while priority_queue:

            current_distance, current_zone = (
                heapq.heappop(priority_queue)
            )

            if current_zone == end:
                break

            if current_distance > distances[current_zone]:
                continue

            for neighbor in self.graph.adjacency[current_zone]:

                neighbor_zone = self.graph.zones[neighbor]

                if neighbor_zone.zone_type == "blocked":
                    continue

                zone_cost = self._zone_cost(
                    neighbor
                )

                traffic_penalty = self._traffic_penalty(
                    neighbor, predicted_usage)

                connection_penalty = self._connection_penalty(
                    current_zone, neighbor
                )

                new_distance = (
                    current_distance
                    + zone_cost
                    + traffic_penalty
                    + connection_penalty
                )

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_zone
                    heapq.heappush(
                        priority_queue,
                        (new_distance, neighbor)
                    )
        if (
            start != end
            and previous[end] is None
        ):
            return []

        return self._build_path(
            previous,
            end
        )

    def _build_path(
        self,
        previous: dict[str, str | None],
        end: str
    ) -> list[str]:
        """Reconstruct a path from Dijkstra's ``previous`` mapping.

        Args:
            previous: Mapping of zone name to the zone it was reached
                from, as built by :meth:`find_path`.
            end: Name of the destination zone to trace back from.

        Returns:
            The list of zone names forming the path, in order from the
            start to ``end``.
        """

        path: list[str] = []

        current = end

        while current is not None:

            path.append(current)

            current = previous[current]

        path.reverse()

        return path
