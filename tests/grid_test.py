"""Unittests for grid"""
#!/usr/bin/env python3

import unittest

from models.grid import Grid


class TestGrid(unittest.TestCase):
    """Grid Test Suite"""

    def test_init(self):
        grid_size = (3, 4)
        capacity = (2, 3)
        grid = Grid(grid_size, capacity)
        self.assertEqual(grid.grid_horizontal_size, 3)
        self.assertEqual(grid.grid_vertical_size, 4)
        self.assertEqual(grid.horizontal_capacity, 2)
        self.assertEqual(grid.vertical_capacity, 3)
        self.assertEqual(grid.number_of_nodes, 12)
        self.assertEqual(grid.number_of_horizontal_edges, 8)
        self.assertEqual(grid.number_of_edges, 17)
        self.assertEqual(grid.congestion, [0] * 17)

    def test_coordinate_is_in_bound(self):
        grid_size = (3, 4)
        capacity = (2, 3)
        grid = Grid(grid_size, capacity)
        self.assertTrue(grid.coordinate_is_in_bound((0, 0)))
        self.assertTrue(grid.coordinate_is_in_bound((2, 3)))
        self.assertFalse(grid.coordinate_is_in_bound((-1, 0)))
        self.assertFalse(grid.coordinate_is_in_bound((0, 4)))
        self.assertFalse(grid.coordinate_is_in_bound((3, 3)))

    def test_get_node_id(self):
        grid_size = (3, 4)
        capacity = (2, 3)
        grid = Grid(grid_size, capacity)
        self.assertEqual(grid.get_node_id((0, 0)), 0)
        self.assertEqual(grid.get_node_id((1, 0)), 1)
        self.assertEqual(grid.get_node_id((2, 0)), 2)
        self.assertEqual(grid.get_node_id((0, 1)), 3)
        self.assertEqual(grid.get_node_id((1, 1)), 4)
        self.assertEqual(grid.get_node_id((2, 1)), 5)
        self.assertEqual(grid.get_node_id((0, 3)), 9)
        self.assertEqual(grid.get_node_id((2, 3)), 11)

    def test_get_edge_cost(self):
        grid_size = (5, 5)
        capacity = (2, 2)
        grid = Grid(grid_size, capacity)
        grid.congestion[0] = 2
        self.assertEqual(grid.get_edge_cost(0), 10000)
        self.assertEqual(grid.get_edge_cost(1), 1.5)

    def test_get_edge_id(self):
        grid_size = (5, 5)
        capacity = (2, 2)
        grid = Grid(grid_size, capacity)
        self.assertEqual(grid.get_edge_id((1, 1), 0), 25)
        self.assertEqual(grid.get_edge_id((1, 1), 1), 5)
        self.assertEqual(grid.get_edge_id((1, 1), 2), 21)
        self.assertEqual(grid.get_edge_id((1, 1), 3), 4)


if __name__ == "__main__":
    unittest.main()
