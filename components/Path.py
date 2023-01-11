from typing import List, Tuple

from Node import Node


class Path:
    def __init__(self, endNode=None) -> None:
        self.coordinates_list: List[Tuple[int, int]] = []
        self.cost: float = 0.0
        self.end_node:Node = endNode
