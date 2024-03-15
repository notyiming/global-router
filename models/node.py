"""Node Module."""

from typing import Tuple


class Node:
    """Node class represents a pin in a net."""

    def __init__(self, prev: "Node", coordinates: Tuple[int, int]):
        self.edge_id = -1
        self.node_id = -1
        self.prev: Node = prev
        self.coordinates: Tuple[int, int] = coordinates
        self.cost = 0.0

    def __lt__(self, other):
        return self.cost < other.cost
