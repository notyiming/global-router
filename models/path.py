"""Path Module"""

from typing import List, Tuple
from models.node import Node


class Path:
    """Path class represents the full path of a net"""

    def __init__(self, end_node) -> None:
        self.coordinates_list: List[Tuple[int, int]] = []
        self.end_node: Node = end_node
        self.edge_id_list: List[int] = []
        self.cost: float = self.end_node.cost

        current_grid = self.end_node

        # traverse node to get full path coordinates
        while current_grid:
            self.coordinates_list.append(current_grid.coordinates)
            self.edge_id_list.append(current_grid.edge_id)
            current_grid = current_grid.prev

        self.edge_id_list.pop()
        self.coordinates_list.reverse()
        self.edge_id_list.reverse()
