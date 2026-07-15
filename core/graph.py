"""Graph data model tying zones and connections together."""

from .zone import Zone
from .connection import Connection


class Graph:
    """The map graph: zones, connections and their adjacency.

    Attributes:
        zones: Mapping of zone name to :class:`Zone` instance.
        connections: List of all :class:`Connection` instances in the
            graph.
        adjacency: Mapping of zone name to the list of directly reachable
            neighbor zone names.
        start_zone: Name of the zone drones start from.
        end_zone: Name of the zone drones must reach.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[str]] = {}

        self.start_zone: str = ""
        self.end_zone: str = ""

    def add_zone(self, zone: Zone) -> None:
        """Register a new zone in the graph.

        Args:
            zone: The zone to add.
        """
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """Register a new connection and update the adjacency list.

        The connection is treated as bidirectional: both zones are added
        to each other's adjacency list.

        Args:
            connection: The connection to add.
        """
        self.connections.append(connection)
        self.adjacency[connection.zone1].append(connection.zone2)
        self.adjacency[connection.zone2].append(connection.zone1)
