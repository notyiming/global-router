"""Node Module"""
from typing import Tuple

class Node:
    """Node Class"""
    def __init__(self, prev, coordinates) -> None:
        self.prev: Node = prev
        self.coordinates: Tuple[int, int] = coordinates
        self.cost = 0.0
        