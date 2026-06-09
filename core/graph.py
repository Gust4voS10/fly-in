from .zone import Zone
from .connection import Connection


class Graph:
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[str]] = {}

        self.start_zone: str = ""
        self.end_zone: str = ""

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []
    
    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)
        self.adjacency[connection.zone1].append(connection.zone2)
        self.adjacency[connection.zone2].append(connection.zone1)