"""Net Module"""

from typing import List, Tuple
from components.path import Path

class Net:
    """Net Class"""
    def __init__(self, net_id, net_name, num_of_pins, pins_coords=[], path=None) -> None:
        self.net_id: int = net_id
        self.net_name: str = net_name
        self.num_of_pins: int = num_of_pins
        self.pins_coords: List[Tuple[int, int]] = pins_coords
        self.path: Path = path