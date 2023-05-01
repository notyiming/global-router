"""Unittests for global router"""
#!/usr/bin/env python3

import unittest

from models.global_router import GlobalRouter
from models.grid import Grid


class TestGlobalRouter(unittest.TestCase):
    """Global Router Test Suite"""
    def setUp(self):
        self.global_router = GlobalRouter(algorithm=1, seed=42)

    def test_init(self):
        self.assertIsNone(self.global_router.grid)
        self.assertEqual(self.global_router.netlist, [])
        self.assertEqual(self.global_router.overflow, 0)
        self.assertEqual(self.global_router.wirelength, 0)
        self.assertEqual(self.global_router.seed, 42)
        self.assertEqual(self.global_router.algorithm, 1)

    def test_get_next_coordinate(self):
        # Test direction 0
        current_node_coordinate = (0, 0)
        next_node_coordinate = self.global_router.get_next_coordinate(
            current_node_coordinate=current_node_coordinate,
            direction=0
        )
        self.assertEqual(next_node_coordinate, (0, 1))

        # Test direction 1
        current_node_coordinate = (0, 0)
        next_node_coordinate = self.global_router.get_next_coordinate(
            current_node_coordinate=current_node_coordinate,
            direction=1
        )
        self.assertEqual(next_node_coordinate, (1, 0))

        # Test direction 2
        current_node_coordinate = (0, 1)
        next_node_coordinate = self.global_router.get_next_coordinate(
            current_node_coordinate=current_node_coordinate,
            direction=2
        )
        self.assertEqual(next_node_coordinate, (0, 0))

        # Test direction 3
        current_node_coordinate = (1, 0)
        next_node_coordinate = self.global_router.get_next_coordinate(
            current_node_coordinate=current_node_coordinate,
            direction=3
        )
        self.assertEqual(next_node_coordinate, (0, 0))

    def test_update_overflow_wirelength_no_overflow(self):
        grid = Grid((3, 4), (2, 3))
        grid.demand = [1] * 17
        self.global_router.grid = grid
        self.assertEqual(grid.number_of_edges, 17)
        self.global_router.update_overflow_wirelength()
        self.assertEqual(self.global_router.overflow, 0)
        self.assertEqual(self.global_router.wirelength, sum(grid.demand))

    def test_update_overflow_wirelength_with_overflow(self):
        grid = Grid((3, 4), (2, 3))
        grid.demand = [5] * 17
        self.global_router.grid = grid
        self.global_router.update_overflow_wirelength()
        self.assertEqual(self.global_router.overflow, 42)
        self.assertEqual(self.global_router.wirelength, sum(grid.demand))


if __name__ == "__main__":
    unittest.main()
