"""Connection (link) data model."""

from dataclasses import dataclass


@dataclass
class Connection:
    """A bidirectional link between two zones.

    Attributes:
        zone1: Name of the first endpoint zone.
        zone2: Name of the second endpoint zone.
        max_link_capacity: Maximum number of drones allowed to cross this
            link during the same turn.
    """
    zone1: str
    zone2: str
    max_link_capacity: int = 1
