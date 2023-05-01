"""Unittests for path"""
#!/usr/bin/env python3

from collections import deque
import unittest
from models.node import Node

from models.path import Path

class TestPath(unittest.TestCase):

    def setUp(self):
        end_node = Node(None, (2, 3))
        self.path = Path(end_node)

    def test_init(self):
        self.assertEqual(self.path.coordinates_list, deque([(2, 3)]))


if __name__ == '__main__':
    unittest.main()