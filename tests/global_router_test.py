"""Unittests for global router"""
#!/usr/bin/env python3

import os
import unittest
from unittest.mock import mock_open, patch

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

    def test_dump_result(self):
        # Test that dump_result writes the correct output file
        self.global_router.parse_input("benchmarks/example.txt")
        self.global_router.route()
        expected_output = "net0 0\n(0, 1, 1)-(1, 1, 1)\n!\nnet1 1\n(0, 2, 1)-(1, 2, 1)\n(1, 2, 1)-(1, 1, 1)\n!\nnet2 2\n(2, 2, 1)-(2, 1, 1)\n(2, 1, 1)-(2, 0, 1)\n(2, 0, 1)-(1, 0, 1)\n!\n"
        output_file_path = "test_output.txt"
        self.global_router.dump_result(output_file_path)
        with open(output_file_path, "r", encoding="UTF-8") as output_file:
            self.assertEqual(output_file.read(), expected_output)
        if os.path.exists("test_output.txt"):
            os.remove("test_output.txt")

    def test_parse_input(self):
        global_router = GlobalRouter((3, 4), (2, 2))
        netlist_details = global_router.parse_input("benchmarks/example.txt")
        self.assertEqual(netlist_details['grid_hor'], 3)
        self.assertEqual(netlist_details['grid_ver'], 3)
        self.assertEqual(netlist_details['ver_cap'], 2)
        self.assertEqual(netlist_details['hor_cap'], 2)
        self.assertEqual(netlist_details['netlist_size'], 3)

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

    def test_generate_congestion_output(self):
        self.global_router.parse_input("benchmarks/example.txt")
        self.global_router.route()
        output_file_path = "test_output.txt"
        figure_file_path = "test_output.txt.fig"
        expected_output = "3 3\n0.0 0.5 0.5 0.0 0.5 0.0 0.0 0.0 0.5 0.5 0.5 0.0 "
        self.global_router.generate_congestion_output(output_file_path)
        with open(figure_file_path, "r", encoding="UTF-8") as output_file:
            self.assertEqual(output_file.read(), expected_output)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        if os.path.exists(figure_file_path):
            os.remove(figure_file_path)


if __name__ == "__main__":
    unittest.main()
