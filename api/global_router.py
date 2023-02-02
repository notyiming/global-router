"""Global Router Module"""

import os
import math
from typing import List
from models.net import Net
from utils import utils


class GlobalRouter:
    """Global Router class, handles the logic of the global router"""

    def __init__(self) -> None:
        self.grid_horizontal_size: int = 0
        self.grid_vertical_size: int = 0
        self.vertical_capacity: int = 0
        self.horizontal_capacity: int = 0
        self.netlist_size: int = 0
        self.netlist: List[Net] = []
        self.total_overflow: int = math.inf
        self.total_wire_length: int = math.inf
        self.number_of_nodes: int = 0
        self.number_of_edges: int = 0
        self.number_of_horizontal_edges: int = 0
        self.demand: List[float] = []

    def show_netlist_info(self) -> None:
        """Prints netlist info to the terminal"""
        print(f"Grid: {self.grid_horizontal_size} x {self.grid_vertical_size}")
        print(f"Vertical Capacity: {self.vertical_capacity}")
        print(f"Horizontal Capacity: {self.horizontal_capacity}")
        print(f"Number of nets: {self.netlist_size}")

    def dump_result(self, output_file_path: str) -> None:
        """Dumps the route result into an output file

        Args:
            output_file_path (str): path of the output file
        """
        file_mode = "x"
        if os.path.exists(output_file_path):
            file_mode = "w"

        with open(output_file_path, file_mode, encoding="UTF-8") as output:
            for net in self.netlist:
                output.write(f"{net.net_name} {net.net_id}\n")
                # path = Path()
                # for i in range(len(coords))
                output.write("!\n")

    def rip_up_and_reroute(self):
        """rip up and reroute"""

    def global_route(self):
        """main global routing logic"""

    def generate_congestion_output(self, output_file_name: str) -> None:
        """Generate the congestion data for the output

        Args:
            output_file_name (str): name of the output file
        """
        with open(f"{output_file_name}.fig", "x", encoding="utf-8") as output:
            output.write(f"{self.grid_horizontal_size} {self.grid_vertical_size}\n")
            for i in range(self.number_of_edges):
                output.write(
                    f"{self.demand[i]/(self.horizontal_capacity if i < self.number_of_horizontal_edges else self.vertical_capacity)} "
                )

    @utils.timeit
    def parse_input(self, input_file_path: str) -> List[Net]:
        """Parse the netlist input file

        Args:
            input_file_path (str): path of the netlist input file

        Raises:
            FileNotFoundError: Input file path not found

        Returns:
            List[Net]: list of all nets
        """
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"{input_file_path} does not exist.")
        with open(input_file_path, "r", encoding="utf-8") as file:
            grid_data = file.readline().split()
            self.grid_horizontal_size = int(grid_data[1])
            self.grid_vertical_size = int(grid_data[2])
            self.vertical_capacity = int(file.readline().split()[2])
            self.horizontal_capacity = int(file.readline().split()[2])
            self.netlist_size = int(file.readline().split()[2])
            for _ in range(self.netlist_size):
                net_info = file.readline().split()
                net_name = net_info[0]
                net_id = int(net_info[1])
                num_of_pins = int(net_info[2])
                net_pins = []
                for _ in range(num_of_pins):
                    net_pin = file.readline().split()
                    net_pin_x = int(net_pin[0])
                    net_pin_y = int(net_pin[1])
                    net_pins.append((net_pin_x, net_pin_y))
                net = Net(net_id, net_name, num_of_pins)
                self.netlist.append(net)
            self.number_of_nodes = self.grid_horizontal_size * self.grid_vertical_size
            self.number_of_horizontal_edges = (
                self.grid_horizontal_size - 1
            ) * self.grid_vertical_size
            self.number_of_edges = (
                self.number_of_horizontal_edges
                + (self.grid_vertical_size - 1) * self.grid_horizontal_size
            )
            self.demand = [0] * self.number_of_edges
            return self.netlist
