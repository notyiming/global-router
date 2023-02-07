"""Global Router Module"""

import heapq
import os
import math
# import random
# import time
from typing import List, Tuple
from models.net import Net
from models.node import Node
from models.path import Path


class GlobalRouter:
    """Global Router class, handles the logic of the global router"""

    def __init__(self) -> None:
        self.grid_horizontal_size: int = 0
        self.grid_vertical_size: int = 0
        self.vertical_capacity: int = 0
        self.horizontal_capacity: int = 0
        self.netlist_size: int = 0
        self.netlist: List[Net] = []
        self.number_of_nodes: int = 0
        self.number_of_edges: int = 0
        self.number_of_horizontal_edges: int = 0
        self.demand: List[float] = []
        # self.seed: int = 0

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
                path = net.path
                coordinates = path.coordinates_list
                for i in range(len(coordinates) - 1):
                    output.write(
                        f"({coordinates[i][0]}, {coordinates[i][1]}, 1)")
                    output.write("-")
                    output.write(
                        f"({coordinates[i+1][0]}, {coordinates[i+1][1]}, 1)\n")
                output.write("!\n")

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

        net.attach_path(Path(best_path))

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
            overflow = self.demand[i] - \
                self.horizontal_capacity if i < self.number_of_horizontal_edges else self.vertical_capacity
            if overflow <= 0:
                continue
            total_overflow += overflow
            max_overflow = max(overflow, max_overflow)
        return (total_overflow, total_wirelength)

    def global_route(self) -> Tuple[int, int]:
        """main global routing logic"""
        cur_seed = 0
        num_init_trials = 10
        seed_feasible = False
        init_wirelength = math.inf
        init_overflow: int = 0

        for _ in range(1 if seed_feasible else num_init_trials):
            # reset to original order
            self.netlist.sort(key=lambda x: x.net_id)

            # random.seed(cur_seed if i == (
            #     1 if seed_feasible else num_init_trials) - 1 else int(time.time()))
            # random.shuffle(self.netlist)
            self.netlist.sort(key=lambda x: x.hpwl)  # sort by its hpwl

            for net in self.netlist:
                if net.num_of_pins == 2:
                    self.route_two_pin_net(net)
                self.update_demand(net.path, True)

            total_overflow, total_wirelength = self.update_overflow()
            if total_overflow <= init_overflow:
                if total_wirelength < init_wirelength or \
                        total_overflow < init_overflow:
                    # self.seed = cur_seed
                    init_overflow = total_overflow
                    init_wirelength = total_wirelength

                    print(
                        f"seed {cur_seed}, overflow: {total_wirelength}, wirelength: {total_wirelength}")

        self.netlist.sort(key=lambda x: x.net_id)  # reset to original order
        return total_overflow, total_wirelength

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
            return self.netlist

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