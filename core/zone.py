from dataclasses import dataclass


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1
