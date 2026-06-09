from collections import deque

from core.graph import Graph


class BFS:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path(
        self,
        start: str,
        end: str
    ) -> list[str]:
        queue = deque([start])
        visited = {start}
        previous: dict[str, str | None] = {
            start: None
        }
        while queue:
            current = queue.popleft()
            if current == end:
                break
            for neighbor in self.graph.adjacency[current]:
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                previous[neighbor] = current
                queue.append(neighbor)
        return self._build_path(
            previous,
            start,
            end
        )
    
    def _build_path(
        self,
        previous: dict[str, str | None],
        start: str,
        end: str
    ) -> list[str]:

        if end not in previous:
            return []

        path = []

        current = end

        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        if path[0] != start:
            return []

        return path
