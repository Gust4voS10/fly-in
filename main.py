from core.graph import Graph
from core.zone import Zone
from core.connection import Connection
from parser.parser import Parse

#graph = Graph()

#graph.add_zone(Zone("hub", 0, 0))
#graph.add_zone(Zone("goal", 10, 10))

#graph.add_connection(Connection("hub", "goal"))

#print(graph.adjacency)

if __name__ == "__main__":
    from algorithms.bfs import BFS
    from parser.parser import Parse

    parser = Parse("01_linear_path.txt")

    graph = parser.parse()

    bfs = BFS(graph)

    path = bfs.find_path(
        graph.start_zone,
        graph.end_zone
    )

    print(path)