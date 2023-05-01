"""Unittests for path"""
#!/usr/bin/env python3

import unittest
from models.net import Net

class TestNet(unittest.TestCase):

    def test_set_hpwl(self):
        net_pins_coordinates = [(0, 0), (2, 3), (5, 1)]
        net = Net(1, "net1", len(net_pins_coordinates), net_pins_coordinates)
        self.assertEqual(net.set_hpwl(), 8)

    def test_init(self):
        net_pins_coordinates = [(0, 0), (2, 3), (5, 1)]
        net = Net(1, "net1", len(net_pins_coordinates), net_pins_coordinates)
        self.assertEqual(net.net_id, 1)
        self.assertEqual(net.net_name, "net1")
        self.assertEqual(net.num_of_pins, 3)
        self.assertEqual(net.net_pins_coordinates, [(0, 0), (2, 3), (5, 1)])
        self.assertIsNone(net.path)
        self.assertEqual(net.hpwl, 8)

if __name__ == '__main__':
    unittest.main()