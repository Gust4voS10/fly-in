import heapq

from core.graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _zone_cost(self, zone_name: str) -> float:
        """
        Returns the traversal cost of a zone.
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

        return predicted_usage.get(
            zone_name,
            0
        ) * 2

    def _connection_penalty(
            self,
            from_zone: str,
            to_zone: str
            ) -> float:

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
        predicted_usage: dict[str, int]
    ) -> list[str]:
        """
        Finds the lowest-cost path using Dijkstra.
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
        """
        Reconstructs the path from the previous dictionary.
        """

        path: list[str] = []

        current = end

        while current is not None:

            path.append(current)

            current = previous[current]

        path.reverse()

        return path
