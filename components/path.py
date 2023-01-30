"""Path Module"""

from typing import List, Tuple
from components.node import Node

class Path:
    """Path Class"""
    def __init__(self, end_node=None) -> None:
        self.coordinates_list: List[Tuple[int, int]] = []
        self.cost: float = 0.0
        self.end_node:Node = end_node
