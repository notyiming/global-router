"""Grid Module"""

from typing import List, Tuple

from models.path import Path
from logs.gr_logger import gr_logger


class Grid:
    """A grid of cells, that represents a layout"""

    def __init__(self, grid_size: Tuple[int, int], capacity: Tuple[int, int]):
        self.grid_horizontal_size: int = grid_size[0]
        self.grid_vertical_size: int = grid_size[1]
        self.horizontal_capacity: int = capacity[0]
        self.vertical_capacity: int = capacity[1]
        self.number_of_nodes: int = self.grid_horizontal_size * \
            self.grid_vertical_size  # total number of cells in the grid
        self.number_of_horizontal_edges: int = (
            self.grid_horizontal_size - 1) * self.grid_vertical_size
        self.number_of_edges: int = (
            self.number_of_horizontal_edges + (self.grid_vertical_size - 1) * self.grid_horizontal_size)
        # the demand of each edge (ver and hor)
        self.demand: List[float] = [0] * self.number_of_edges

    def is_overflow(self, path: Path) -> bool:
        """Determines if overflow exists for a path

        Args:
            path (Path): layout path

        Returns:
            bool: layout has overflow
        """
        for edge_id in path.edge_id_set:
            if self.demand[edge_id] > self.horizontal_capacity \
                    if edge_id < self.number_of_horizontal_edges else self.vertical_capacity:
                return True
        return False

    def update_demand(self, path: Path, increment: bool):
        """Update demand level for the path

        Args:
            path (Path): path
            increment (bool): demand is incremented, else decremented
        """
        for edge_id in path.edge_id_set:
            if increment:  # place wire
                self.demand[edge_id] += 1
            else:  # remove wire
                self.demand[edge_id] -= 1

    def get_edge_cost(self, edge_id: int) -> float:
        """Get the cost of the edge. This cost function ensures that edges with high demand
        have higher costs, which guides the search algorithm towards less congested paths
        and helps find a solution more quickly.

        Args:
            edge_id (int): Edge ID

        Returns:
            float: cost of the edge
        """
        capacity = self.horizontal_capacity if edge_id < self.number_of_horizontal_edges else self.vertical_capacity
        if self.demand[edge_id] >= capacity:  # if the edge is overflown
            return 10000
        return 1 + (self.demand[edge_id] + 1) / capacity

    def get_edge_id(self, coordinate: Tuple[int, int], direction: int) -> int:
        """Get ID of the edge

        Args:
            coordinate (Tuple[int, int]): coordinate of the node
            direction (int): direction

        Returns:
            int: Edge ID
        """
        match direction:
            case 0:
                return self.number_of_horizontal_edges + (self.grid_horizontal_size - 1) \
                    * coordinate[1] + coordinate[0]
            case 1:
                return (self.grid_horizontal_size - 1) * coordinate[1] + coordinate[0]
            case 2:
                return self.number_of_horizontal_edges + (self.grid_horizontal_size - 1) \
                    * (coordinate[1] - 1) + coordinate[0]
            case 3:
                return (self.grid_horizontal_size - 1) * coordinate[1] + (coordinate[0] - 1)

    def get_node_id(self, coordinate: Tuple[int, int]) -> int:
        """Get ID of the node

        Args:
            coordinate (Tuple[int, int]): the coordinate of the node

        Returns:
            int: the ID of the node
        """
        return self.grid_horizontal_size * coordinate[1] + coordinate[0]

    def coordinate_is_legal(self, next_coordinate: Tuple[int, int]) -> bool:
        """Determine if given coordinate is within layout bounds

        Args:
            next_coordinate (Tuple[int, int]): coordinate of next node

        Returns:
            bool: coordinate of next node is legal or not
        """
        if next_coordinate[0] < 0 or next_coordinate[0] >= self.grid_horizontal_size:
            return False
        if next_coordinate[1] < 0 or next_coordinate[1] >= self.grid_vertical_size:
            return False
        return True
