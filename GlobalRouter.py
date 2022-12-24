import os
from typing import List, Tuple

class GlobalRouter:
    """Global Router class, handles the logic of the global router"""

    def __init__(self) -> None:
        self.grid_horizontal_size = 0
        self.grid_vertical_size = 0
        self.vertical_capacity = 0
        self.horizontal_capacity = 0
        self.netlist_size = 0
        self.netlist = []

    def parse_input(self, file_path: str) -> List[Tuple]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} does not exist.")
        with open(file_path, "r") as input:
            grid_data = input.readline().split()
            self.grid_horizontal_size = int(grid_data[1])
            self.grid_vertical_size = int(grid_data[2])
            self.vertical_capacity = int(input.readline().split()[2])
            self.horizontal_capacity = int(input.readline().split()[2])
            netlist_size = int(input.readline().split()[2])
            for _ in range(netlist_size):
                net_info = input.readline().split()
                net_name = net_info[0]
                net_id = int(net_info[1])
                num_of_pins = int(net_info[2])
                net_pins = []
                for _ in range(num_of_pins):
                    net_pin = input.readline().split()
                    net_pin_x = int(net_pin[0])
                    net_pin_y = int(net_pin[1])
                    net_pins.append((net_pin_x, net_pin_y))
                self.netlist.append((net_name, net_id, num_of_pins, net_pins))
            return self.netlist
            