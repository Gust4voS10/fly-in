import heapq

from core.graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _zone_cost(self, zone_name: str) -> int:

        zone = self.graph.zones[zone_name]

        if zone.zone_type == "restricted":
            return 2

        return 1

    def find_path(
        self,
        start: str,
        end: str
    ) -> list[str]:
        # distances: best known cost to each zone
        distances: dict[str, int] = {
            zone_name: float("inf")
            for zone_name in self.graph.zones
        }

        # hops: number of edges from start to zone for tie-breaking
        hops: dict[str, int] = {
            zone_name: float("inf")
            for zone_name in self.graph.zones
        }

        previous: dict[str, str | None] = {
            zone_name: None
            for zone_name in self.graph.zones
        }

        distances[start] = 0
        hops[start] = 0

        # priority queue entries: (distance, hops, zone)
        priority_queue: list[tuple[int, int, str]] = [
            (0, 0, start)
        ]

        while priority_queue:

            current_distance, current_hops, current_zone = (
                heapq.heappop(priority_queue)
            )

            if current_zone == end:
                break

            # skip outdated entries
            if (
                current_distance > distances[current_zone]
                or (
                    current_distance == distances[current_zone]
                    and current_hops > hops[current_zone]
                )
            ):
                continue

            for neighbor in self.graph.adjacency[current_zone]:

                cost = self._zone_cost(neighbor)

                new_distance = current_distance + cost
                new_hops = current_hops + 1

                # update when strictly better cost, or equal cost but fewer hops
                if (
                    new_distance < distances[neighbor]
                    or (
                        new_distance == distances[neighbor]
                        and new_hops < hops[neighbor]
                    )
                ):

                    distances[neighbor] = new_distance
                    hops[neighbor] = new_hops
                    previous[neighbor] = current_zone

                    heapq.heappush(
                        priority_queue,
                        (new_distance, new_hops, neighbor)
                    )

        return self._build_path(previous, end)

    def _build_path(
        self,
        previous: dict[str, str | None],
        end: str
    ) -> list[str]:

        path: list[str] = []

        current = end

        while current is not None:

            path.append(current)

            current = previous[current]

        path.reverse()

        return path