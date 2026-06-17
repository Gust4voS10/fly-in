import heapq

from core.graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _zone_cost(self, zone_name: str) -> int:
        """
        Returns the traversal cost of a zone.
        """

        zone = self.graph.zones[zone_name]

        if zone.zone_type == "restricted":
            return 2

        return 1

    def find_path(
        self,
        start: str,
        end: str
    ) -> list[str]:
        """
        Finds the lowest-cost path using Dijkstra.
        """

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

                cost = self._zone_cost(
                    neighbor
                )

                new_distance = (
                    current_distance + cost
                )

                if new_distance < distances[neighbor]:

                    distances[neighbor] = (
                        new_distance
                    )

                    previous[neighbor] = (
                        current_zone
                    )

                    heapq.heappush(
                        priority_queue,
                        (
                            new_distance,
                            neighbor
                        )
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
