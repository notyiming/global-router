"""Node Module"""
import math
from typing import Tuple, List


class Node:
    """Node class represents a pin in a net"""

    def __init__(self, prev, coordinates) -> None:
        self.edge_id = -1
        self.node_id = -1
        self.prev: Node = prev
        self.coordinates: Tuple[int, int] = coordinates
        self.cost = 0.0

    def __lt__(self, other):
        return self.cost < other.cost

    def set_node_id(self, grid_horizontal_size: int):
        """Set ID of the node based on grid layout

        Args:
           grid_horizontal_size (int): the horizontal size of the grid
        """
        self.node_id = grid_horizontal_size * self.coordinates[1] + self.coordinates[0]

    def calculate_cost(self, grid_info: Tuple[List[float], int, int, int]) -> float:
        """Get the cost of the edge

        Args:
            grid_info (Tuple[List[float], int, int, int]): Demand, Grid Horizontal Capacity,
            Grid Vertical Capacity, Number of Horizontal Edges

        Returns:
            float: cost
        """
        demand = grid_info[0]
        hor_cap = grid_info[1]
        ver_cap = grid_info[2]
        num_of_hor_edges = grid_info[3]

        capacity = hor_cap if self.edge_id < num_of_hor_edges else ver_cap
        if demand[self.edge_id] < capacity:
            return 1.0 + (demand[self.edge_id] + 1) / capacity
        else:
            return math.inf
