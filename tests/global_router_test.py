"""Unittests"""
#!/usr/bin/env python3

import unittest

from models.global_router import GlobalRouter


class TestGlobalRouter(unittest.TestCase):
    """Global Router Test Suite"""
    def test_parse_input(self):
        """test parse input"""
        # GlobalRouter.parse_input()

    def test_global_router_instance(self):
        """test global router class instance"""
        self.assertIsInstance(GlobalRouter(), GlobalRouter)

if __name__ == "__main__":
    unittest.main()
