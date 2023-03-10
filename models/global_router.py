"""Global Router Module"""

import heapq
import os
import random
from typing import List, Tuple
import click
from models.net import Net
from models.node import Node
from models.path import Path
from logs.gr_logger import gr_logger
from util import util


class GlobalRouter:
    """Global Router class, handles the logic of the global router"""

    def __init__(self) -> None:
        self.grid_horizontal_size: int = 0
        self.grid_vertical_size: int = 0
        self.vertical_capacity: int = 0
        self.horizontal_capacity: int = 0
        self.netlist: List[Net] = []
        self.number_of_nodes: int = 0
        self.number_of_edges: int = 0
        self.overflow: int = 0
        self.wirelength: int = 0
        self.number_of_horizontal_edges: int = 0
        self.demand: List[float] = []

    @util.log_func
    def show_netlist_info(self) -> None:
        """Prints netlist info to the terminal"""
        gr_logger.info(
            "\nLayout and Netlist Details\n"
            "==========================\n"
            f"Grid: {self.grid_horizontal_size} x {self.grid_vertical_size}\n"
            f"Vertical Capacity: {self.vertical_capacity}\n"
            f"Horizontal Capacity: {self.horizontal_capacity}\n"
            f"Number of nets: {len(self.netlist)}\n"
        )

    @util.log_func
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
                path = net.path
                coordinates = path.coordinates_list
                for i in range(len(coordinates) - 1):
                    output.write(
                        f"({coordinates[i][0]}, {coordinates[i][1]}, 1)")
                    output.write("-")
                    output.write(
                        f"({coordinates[i+1][0]}, {coordinates[i+1][1]}, 1)\n")
                output.write("!\n")
            gr_logger.info(
                f"Output successfully dumped into {output_file_path}")

    @util.timeit
    @util.log_func
    def rip_up_and_reroute(self):
        """rip up and reroute"""

    def get_next_coordinate(
        self,
        current_node_coordinate: Tuple[int, int],
        direction: int
    ) -> Tuple[int, int]:
        """ Get next coordinate for the path, given the
        current node

        Args:
            current_node_coordinate (Tuple[int, int]): coordinate of current node
            direction (int): direction to next node's coordinate

        Returns:
            Tuple[int, int]: next node's coordinate
        """
        match direction:
            case 0:
                return current_node_coordinate[0], current_node_coordinate[1] + 1
            case 1:
                return current_node_coordinate[0] + 1, current_node_coordinate[1]
            case 2:
                return current_node_coordinate[0], current_node_coordinate[1] - 1
            case 3:
                return current_node_coordinate[0] - 1, current_node_coordinate[1]

    def coordinate_is_legal(self, next_coordinate: Tuple[int, int]) -> bool:
        """Determine if given coordinate is within layout bounds

        Args:
            next_coordinate (Tuple[int, int]): coordinate of next node

        Returns:
            bool: coordinate of next node is legal or not
        """
        if next_coordinate[0] < 0 or next_coordinate[0] >= self.grid_horizontal_size:
            return False
        if next_coordinate[1] < 0 or next_coordinate[1] >= self.grid_vertical_size:
            return False
        return True

    def get_node_id(self, coordinate: Tuple[int, int]) -> int:
        """Get ID of the node

        Args:
            coordinate (Tuple[int, int]): the coordinate of the node

        Returns:
            int: the ID of the node
        """
        return self.grid_horizontal_size * coordinate[1] + coordinate[0]

    def get_edge_id(self, coordinate: Tuple[int, int], direction: int) -> int:
        """Get ID of the edge

        Args:
            coordinate (Tuple[int, int]): coordinate of the node
            direction (int): direction

        Returns:
            int: Edge ID
        """
        match direction:
            case 0:
                return self.number_of_horizontal_edges + (self.grid_horizontal_size - 1) \
                    * coordinate[1] + coordinate[0]
            case 1:
                return (self.grid_horizontal_size - 1) * coordinate[1] + coordinate[0]
            case 2:
                return self.number_of_horizontal_edges + (self.grid_horizontal_size - 1) \
                    * (coordinate[1] - 1) + coordinate[0]
            case 3:
                return (self.grid_horizontal_size - 1) * coordinate[1] + (coordinate[0] - 1)

    def get_edge_cost(self, edge_id: int) -> float:
        """Get the cost of the edge

        Args:
            edge_id (int): Edge ID

        Returns:
            float: cost of the edge
        """
        capacity = self.horizontal_capacity if edge_id < self.number_of_horizontal_edges else self.vertical_capacity
        if self.demand[edge_id] < capacity:
            return 1.0 + (self.demand[edge_id] + 1) / capacity
        return 1e4

    def route_two_pin_net(self, net: Net):
        """Route a two-pin net (BFS)

        Args:
            net (Net): two-pin net
        """
        start_pin = net.net_pins_coordinates[0]
        end_pin = net.net_pins_coordinates[1]

        node = Node(None, start_pin)
        node.node_id = self.get_node_id(node.coordinates)

        priority_queue = []
        heapq.heapify(priority_queue)
        heapq.heappush(priority_queue, node)

        node_used = [False] * self.number_of_nodes
        best_path = None

        while priority_queue:
            current_node: Node = heapq.heappop(priority_queue)

            if node_used[current_node.node_id]:
                continue
            node_used[current_node.node_id] = True

            if current_node.coordinates == end_pin:
                best_path = current_node
                break

            for i in range(4):  # bfs (all direction)
                next_coordinate = self.get_next_coordinate(
                    current_node.coordinates, i)
                if not self.coordinate_is_legal(next_coordinate):
                    continue
                next_node = Node(current_node, next_coordinate)

                # set edge ID
                next_node.edge_id = self.get_edge_id(
                    current_node.coordinates, i)

                # set node ID
                next_node.node_id = self.get_node_id(
                    next_node.coordinates)  # or next_coordinates?

                # set cost
                next_node.cost = current_node.cost + \
                    self.get_edge_cost(next_node.edge_id)

                heapq.heappush(priority_queue, next_node)

        net.path = Path(best_path)

    def update_demand(self, path: Path, increment: bool):
        """Update demand level for the path

        Args:
            path (Path): path
            increment (bool): demand is incremented
        """
        for edge_id in path.edge_id_list:
            if increment:
                self.demand[edge_id] += 1
            else:
                self.demand[edge_id] -= 1

    def update_overflow(self) -> Tuple[int, int]:
        """Update overflow info for the layout

        Returns:
            Tuple[int, int]: (total_overflow, wirelength)
        """
        max_overflow = 0
        total_overflow = 0
        total_wirelength = 0
        overflow = 0
        for i in range(self.number_of_edges):
            total_wirelength += self.demand[i]
            capacity = self.vertical_capacity
            if i < self.number_of_horizontal_edges:
                capacity = self.horizontal_capacity
            overflow = self.demand[i] - capacity
            if overflow <= 0:
                continue
            total_overflow += overflow
            max_overflow = max(overflow, max_overflow)
        return (total_overflow, total_wirelength)

    @util.timeit
    @util.log_func
    def global_route(self):
        """main global routing logic"""
        random.shuffle(self.netlist)
        self.netlist.sort(key=lambda x: x.hpwl)

        with click.progressbar(self.netlist, label="Routing the netlist") as netlist:
            for net in netlist:
                self.route_two_pin_net(net)
                self.update_demand(net.path, True)

        total_overflow, total_wirelength = self.update_overflow()
        gr_logger.info(f"Total Overflow: {total_overflow}")
        gr_logger.info(f"Total Wirelength: {total_wirelength}")
        self.overflow = total_overflow
        self.wirelength = total_wirelength

    def generate_congestion_output(self, output_file_name: str) -> None:
        """Generate the congestion data for the output

        Args:
            output_file_name (str): name of the output file
        """
        file_mode = "x"
        if os.path.exists(output_file_name):
            file_mode = "w"

        with open(f"{output_file_name}.fig", file_mode, encoding="utf-8") as output:
            output.write(
                f"{self.grid_horizontal_size} {self.grid_vertical_size}\n")
            for i in range(self.number_of_edges):
                output.write(
                    f"{self.demand[i]/(self.horizontal_capacity if i < self.number_of_horizontal_edges else self.vertical_capacity)} "
                )
            gr_logger.info(f"Congestion data generated into {output_file_name}.fig")

    @util.log_func
    def parse_input(self, input_file_path: str):
        """Parse the netlist input file

        Args:
            input_file_path (str): path of the netlist input file

        Raises:
            FileNotFoundError: Input file path not found

        Returns:
            List[Net]: list of all nets
        """
        with open(input_file_path, "r", encoding="utf-8") as file:
            grid_data = file.readline().split()
            self.grid_horizontal_size = int(grid_data[1])
            self.grid_vertical_size = int(grid_data[2])
            self.vertical_capacity = int(file.readline().split()[2])
            self.horizontal_capacity = int(file.readline().split()[2])
            netlist_size = int(file.readline().split()[2])
            for _ in range(netlist_size):
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
                net = Net(net_id, net_name, num_of_pins, net_pins)
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
            gr_logger.info(
                f"{input_file_path} parsed successfully, data structures created")
            netlist_details = {}
            netlist_details["grid_hor"] = self.grid_horizontal_size
            netlist_details["grid_ver"] = self.grid_vertical_size
            netlist_details["ver_cap"] = self.vertical_capacity
            netlist_details["hor_cap"] = self.horizontal_capacity
            netlist_details["netlist_size"] = netlist_size
            return netlist_details

    def is_overflow(self, path: Path) -> bool:
        """Determines if overflow exists for a path

        Args:
            path (Path): layout path

        Returns:
            bool: layout has overflow
        """
        for edge_id in path.edge_id_list:
            if self.demand[edge_id] > self.horizontal_capacity \
                    if edge_id < self.number_of_horizontal_edges else self.vertical_capacity:
                return True
        return False
