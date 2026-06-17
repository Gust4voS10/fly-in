from dataclasses import dataclass


@dataclass
class Drone:
    visual_x = 0.0
    visual_y = 0.0
    target_x = 0.0
    target_y = 0.0
    drone_id: int
    current_zone: str
    path_index: int = 0
    delivered: bool = False
    remaining_turns: int = 0
