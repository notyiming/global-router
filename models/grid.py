"""Grid Module."""

from typing import List, Tuple

from models.path import Path


class Grid:
    """A grid of cells, that represents a layout."""

    def __init__(self, grid_size: Tuple[int, int], capacity: Tuple[int, int]):
        self.grid_horizontal_size: int = grid_size[0]
        self.grid_vertical_size: int = grid_size[1]
        self.horizontal_capacity: int = capacity[0]
        self.vertical_capacity: int = capacity[1]
        self.number_of_nodes: int = (
            self.grid_horizontal_size * self.grid_vertical_size
        )  # total number of cells in the grid
        self.number_of_horizontal_edges: int = (
            self.grid_horizontal_size - 1
        ) * self.grid_vertical_size
        self.number_of_edges: int = (
            self.number_of_horizontal_edges
            + (self.grid_vertical_size - 1) * self.grid_horizontal_size
        )
        # the congestion of each edge (ver and hor)
        self.congestion: List[float] = [0] * self.number_of_edges

    def is_overflow(self, path: Path) -> bool:
        """Determine if overflow exists for a path.

        Attributes
        ----------
        path: Path
            Layout path.

        Returns
        -------
        bool
            Layout has overflow.

        """
        for edge_id in path.edge_id_set:
            if (
                self.congestion[edge_id] > self.horizontal_capacity
                if edge_id < self.number_of_horizontal_edges
                else self.vertical_capacity
            ):
                return True
        return False

    def update_congestion(self, path: Path, increment: bool):
        """Update congestion level for the path.

        Attributes
        ----------
        path: Path
            Routing path.
        increment: bool
            Congestion is incremented, else decremented.

        """
        for edge_id in path.edge_id_set:
            if increment:  # place wire
                self.congestion[edge_id] += 1
            else:  # remove wire
                self.congestion[edge_id] -= 1

    def get_edge_cost(self, edge_id: int) -> float:
        """Get the cost of the edge. This cost function ensures that edges with high\
        congestion have higher costs, which guides the search algorithm towards less\
        congested paths and helps find a solution more quickly.

        Attributes
        ----------
        edge_id: int
            Edge ID

        Returns
        -------
        float
            Cost of the edge.

        """
        capacity = (
            self.horizontal_capacity
            if edge_id < self.number_of_horizontal_edges
            else self.vertical_capacity
        )
        if self.congestion[edge_id] >= capacity:  # if the edge is overflown
            return 10000
        return 1 + (self.congestion[edge_id] + 1) / capacity

    def get_edge_id(self, coordinate: Tuple[int, int], direction: int) -> int:
        """Get ID of the edge.

        Attributes
        ----------
        coordinate: Tuple[int, int]
            Coordinate of the node.
        direction: int
            Direction

        Returns
        -------
        int
            Edge ID

        """
        match direction:
            case 0:
                return (
                    self.number_of_horizontal_edges
                    + (self.grid_horizontal_size - 1) * coordinate[1]
                    + coordinate[0]
                )
            case 1:
                return (self.grid_horizontal_size - 1) * coordinate[1] + coordinate[0]
            case 2:
                return (
                    self.number_of_horizontal_edges
                    + (self.grid_horizontal_size - 1) * (coordinate[1] - 1)
                    + coordinate[0]
                )
            case 3:
                return (self.grid_horizontal_size - 1) * coordinate[1] + (
                    coordinate[0] - 1
                )

    def get_node_id(self, coordinate: Tuple[int, int]) -> int:
        """Get ID of the node.

        Attributes
        ----------
        coordinate: Tuple[int, int]
            The coordinate of the node.

        Returns
        -------
        int
            The ID of the node.

        """
        return self.grid_horizontal_size * coordinate[1] + coordinate[0]

    def coordinate_is_in_bound(self, next_coordinate: Tuple[int, int]) -> bool:
        """Determine if given coordinate is within layout bounds.

        Attributes
        ----------
        next_coordinate: Tuple[int, int]
            Coordinate of next node.

        Returns
        -------
        bool
            Coordinate of next node is legal or not.

        """
        x, y = next_coordinate
        return 0 <= x < self.grid_horizontal_size and 0 <= y < self.grid_vertical_size
