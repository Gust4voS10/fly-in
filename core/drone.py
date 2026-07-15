"""Drone data model."""

from dataclasses import dataclass


@dataclass
class Drone:
    """A single drone traveling through the graph.

    Attributes:
        visual_x: Current animated X position used purely for rendering
            (eases toward ``target_x`` every frame).
        visual_y: Current animated Y position used purely for rendering
            (eases toward ``target_y`` every frame).
        target_x: X coordinate the drone's visual position is easing
            toward.
        target_y: Y coordinate the drone's visual position is easing
            toward.
        drone_id: Unique identifier of the drone.
        current_zone: Name of the zone the drone currently occupies.
        path_index: Index of ``current_zone`` within the drone's
            precomputed path.
        delivered: Whether the drone has reached the end of its path
            (goal in forward mode, start in reverse mode).
        remaining_turns: Number of turns the drone must still wait before
            it can move again (used when crossing ``restricted`` zones).
        reverse_mode: Whether the drone is currently retracing its path
            back toward the start.
    """
    visual_x = 0.0
    visual_y = 0.0
    target_x = 0.0
    target_y = 0.0
    drone_id: int
    current_zone: str
    path_index: int = 0
    delivered: bool = False
    remaining_turns: int = 0
    reverse_mode: bool = False
