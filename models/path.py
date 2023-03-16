"""Path Module"""

from collections import deque
from typing import Tuple, Deque
from models.node import Node


class Path:
    """Path class represents the full path of a net"""

    def __init__(self, end_node) -> None:
        self.coordinates_list: Deque[Tuple[int, int]] = deque()
        self.end_node: Node = end_node
        self.edge_id_list: Deque[int] = deque()

        current_grid = self.end_node

        # traverse node to get full path coordinates
        while current_grid:
            self.coordinates_list.appendleft(current_grid.coordinates)
            self.edge_id_list.appendleft(current_grid.edge_id)
            current_grid = current_grid.prev

        self.edge_id_list.popleft()
