"""Zone (hub) data model."""

from dataclasses import dataclass


@dataclass
class Zone:
    """A single hub/zone on the map.

    Attributes:
        name: Unique identifier of the zone.
        x: X coordinate on the map grid.
        y: Y coordinate on the map grid.
        zone_type: One of ``"normal"``, ``"priority"``, ``"restricted"`` or
            ``"blocked"``. Affects pathfinding cost and traversal rules.
        color: Display color name used by the renderer.
        max_drones: Maximum number of drones allowed in this zone at the
            same time.
    """
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1
