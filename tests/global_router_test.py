import unittest
from components.GlobalRouter import GlobalRouter

class TestGlobalRouter(unittest.TestCase):
    def test_parse_input(self):
        ...
        # GlobalRouter.parse_input()
    
    def test_global_router_instance(self):
        self.assertIsInstance(GlobalRouter(), GlobalRouter)

if __name__ == "__main__":
    unittest.main()