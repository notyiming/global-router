"""Net Module."""

import math
from typing import List, Tuple

from models.path import Path


class Net:
    """Net class represents a wire that connects two or more pins."""

    def __init__(self, net_id, net_name, num_of_pins, net_pins_coordinates):
        self.net_id: int = net_id
        self.net_name: str = net_name
        self.num_of_pins: int = num_of_pins
        self.net_pins_coordinates: List[Tuple[int, int]] = net_pins_coordinates
        self.path: Path = None
        self.hpwl: int = self.set_hpwl()

    def set_hpwl(self) -> int:
        """Set the value of HPWL (Half-Perimeter Wirelength).

        Returns
        -------
        int
            HPWL (Half-Perimeter Wirelength).

        """
        min_x = math.inf
        min_y = math.inf
        max_x = 0
        max_y = 0
        for coordinate in self.net_pins_coordinates:
            min_x = min(coordinate[0], min_x)
            min_y = min(coordinate[1], min_y)
            max_x = max(coordinate[0], max_x)
            max_y = max(coordinate[1], max_y)
        return (max_x - min_x) + (max_y - min_y)
