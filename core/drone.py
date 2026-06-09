from dataclasses import dataclass


@dataclass
class Drone:
    drone_id: int
    current_zone:str
    path_index: int = 0
    delivered: bool = False
    remaining_turns: int = 0