"""Global Router Module"""

from collections import deque
import heapq
import os
import random
from typing import List, Tuple
import fibheap
import click
from models.net import Net
from models.node import Node
from models.path import Path
from models.grid import Grid
from logs.gr_logger import gr_logger
from util import util


class GlobalRouter:
    """Global Router class, handles the logic of the global router"""

    def __init__(self, algorithm: int, seed: int) -> None:
        self.grid: Grid = None
        self.netlist: List[Net] = []
        self.overflow: int = 0  # total number of overflow in the layout
        self.wirelength: int = 0  # total wirelength in the layout
        self.seed: int = seed # seed for random number generator
        self.algorithm: int = algorithm

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
                coordinates = net.path.coordinates_list
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
        overflow_nets: List[Net] = []
        grid = self.grid
        for net in self.netlist:
            if grid.is_overflow(net.path):
                overflow_nets.append(net)

        random.shuffle(overflow_nets)
        # overflow_nets.sort(key=lambda x: x.hpwl)
        match self.algorithm:
            case 1:
                routing_algorithm = self.connect_net_best_first_search_heapq
            case 2:
                routing_algorithm = self.connect_net_best_first_search_fibheap
            case 3:
                routing_algorithm = self.connect_net_breadth_first_search

        with click.progressbar(overflow_nets, label="Performing Rip-up and Reroute") as nets:
            for net in nets:
                grid.update_demand(net.path, False)  # removing the path
                routing_algorithm(net)  # rerouting the path
                grid.update_demand(net.path, True)  # replacing the path

        self.update_overflow_wirelength()
        return self.overflow, self.wirelength

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

    def connect_net_breadth_first_search(self, net: Net):
        """Route a two-pin net with Breadth-First Search

        This will only create L-shaped paths for all nets.
        This is a terrible algorithm as it doesn't take
        congestion into account and might create a lot of overflow.

        Args:
            net (Net): two-pin net
        """
        grid = self.grid
        start_pin = net.net_pins_coordinates[0]
        end_pin = net.net_pins_coordinates[1]

        node = Node(None, start_pin)
        node.node_id = grid.get_node_id(node.coordinates)

        queue = deque([node])

        visited_nodes = set()

        while queue:
            current_node: Node = queue.popleft()

            # base case: current node is the end pin
            if current_node.coordinates == end_pin:
                net.path = Path(current_node)
                break

            # skip if current node is already visited
            if current_node.node_id in visited_nodes:
                continue
            visited_nodes.add(current_node.node_id)

            # add neighbors in all directions to priority queue
            for i in range(4):
                next_coordinate = self.get_next_coordinate(
                    current_node.coordinates, i)
                next_node_id = grid.get_node_id(next_coordinate)

                # check if neighbor node coordinate is legal and if neighbor node is visited
                if not grid.coordinate_is_legal(next_coordinate) or next_node_id in visited_nodes:
                    continue

                next_node = Node(current_node, next_coordinate)

                # set node ID
                next_node.node_id = next_node_id

                # set edge ID
                next_node.edge_id = grid.get_edge_id(
                    current_node.coordinates, i)

                # set cost
                # next_node.cost = current_node.cost + \
                #     grid.get_edge_cost(next_node.edge_id, False)

                queue.append(next_node)

    def connect_net_best_first_search_heapq(self, net: Net):
        """Route a two-pin net with Best-First Search
        
        The priority queue (binary heap) stores the nodes to be 
        expanded in ascending order of their congestion heuristic
        cost. At each step, the algorithm chooses the node with 
        the lowest cost and expands it by considering all of its 
        neighbors.


        Args:
            net (Net): two-pin net
        """
        grid = self.grid
        start_pin = net.net_pins_coordinates[0]
        end_pin = net.net_pins_coordinates[1]

        node = Node(None, start_pin)
        node.node_id = grid.get_node_id(node.coordinates)

        priority_queue = []
        heapq.heapify(priority_queue)
        heapq.heappush(priority_queue, node)

        visited_nodes = set()

        while priority_queue:
            current_node: Node = heapq.heappop(priority_queue)

            # base case: current node is the end pin
            if current_node.coordinates == end_pin:
                net.path = Path(current_node)
                break

            # skip if current node is already visited
            if current_node.node_id in visited_nodes:
                continue
            visited_nodes.add(current_node.node_id)

            # add neighbors in all directions to priority queue
            for i in range(4):
                next_coordinate = self.get_next_coordinate(
                    current_node.coordinates, i)
                next_node_id = grid.get_node_id(next_coordinate)

                # check if neighbor node coordinate is legal and if neighbor node is visited
                if not grid.coordinate_is_legal(next_coordinate) or next_node_id in visited_nodes:
                    continue

                next_node = Node(current_node, next_coordinate)

                # set node ID
                next_node.node_id = next_node_id

                # set edge ID
                next_node.edge_id = grid.get_edge_id(
                    current_node.coordinates, i)

                # set cost
                next_node.cost = current_node.cost + \
                    grid.get_edge_cost(next_node.edge_id)

                heapq.heappush(priority_queue, next_node)

    def connect_net_best_first_search_fibheap(self, net: Net):
        """Route a two-pin net with Best-First Search
        
        The priority queue (Fibonacci heap) stores the nodes to be 
        expanded in ascending order of their congestion heuristic
        cost. At each step, the algorithm chooses the node with 
        the lowest cost and expands it by considering all of its 
        neighbors.


        Args:
            net (Net): two-pin net
        """
        grid = self.grid
        start_pin = net.net_pins_coordinates[0]
        end_pin = net.net_pins_coordinates[1]

        node = Node(None, start_pin)
        node.node_id = grid.get_node_id(node.coordinates)

        heap = fibheap.makefheap()
        fibheap.fheappush(heap, node)

        visited_nodes = set()
        best_path = None

        while heap:
            current_node = fibheap.fheappop(heap)

            if current_node.node_id in visited_nodes:
                continue
            visited_nodes.add(current_node.node_id)

            if current_node.coordinates == end_pin:
                best_path = current_node
                break

            for i in range(4):  # bfs (all direction)
                next_coordinate = self.get_next_coordinate(
                    current_node.coordinates, i)
                if not grid.coordinate_is_legal(next_coordinate):
                    continue
                next_node = Node(current_node, next_coordinate)

                # set edge ID
                next_node.edge_id = grid.get_edge_id(
                    current_node.coordinates, i)

                # set node ID
                next_node.node_id = grid.get_node_id(
                    next_node.coordinates)  # or next_coordinates?

                # set cost
                next_node.cost = current_node.cost + \
                    grid.get_edge_cost(next_node.edge_id)

                fibheap.fheappush(heap, next_node)

        net.path = Path(best_path)

    def update_overflow_wirelength(self) -> Tuple[int, int]:
        """Update overflow and wirelength for the layout"""
        total_overflow = 0
        total_wirelength = 0
        overflow = 0
        grid = self.grid
        for i in range(grid.number_of_edges):
            # get wirelength from demand list
            total_wirelength += grid.demand[i]
            capacity = grid.vertical_capacity
            if i < grid.number_of_horizontal_edges:
                capacity = grid.horizontal_capacity
            overflow = grid.demand[i] - capacity
            if overflow <= 0:
                continue
            total_overflow += overflow
        self.overflow = total_overflow
        self.wirelength = total_wirelength

    @util.timeit
    @util.log_func
    def route(self):
        """main global routing logic"""
        random.shuffle(self.netlist)
        self.netlist.sort(key=lambda x: x.hpwl)

        match self.algorithm:
            case 1:
                routing_algorithm = self.connect_net_best_first_search_heapq
            case 2:
                routing_algorithm = self.connect_net_best_first_search_fibheap
            case 3:
                routing_algorithm = self.connect_net_breadth_first_search

        with click.progressbar(self.netlist, label="Routing the netlist") as netlist:
            for net in netlist:
                routing_algorithm(net)
                self.grid.update_demand(net.path, True)

        self.update_overflow_wirelength()
        gr_logger.info(f"Total Overflow: {self.overflow}")
        gr_logger.info(f"Total Wirelength: {self.wirelength}")
        self.netlist.sort(key=lambda x: x.net_id)

    def generate_congestion_output(self, output_file_name: str):
        """Generate the congestion data for the output

        Args:
            output_file_name (str): name of the output file
        """
        file_mode = "x"
        if os.path.exists(output_file_name):
            file_mode = "w"

        with open(f"{output_file_name}.fig", file_mode, encoding="utf-8") as output:
            grid = self.grid
            output.write(
                f"{grid.grid_horizontal_size} {grid.grid_vertical_size}\n")
            for i in range(grid.number_of_edges):
                output.write(
                    f"{grid.demand[i]/(grid.horizontal_capacity if i < grid.number_of_horizontal_edges else grid.vertical_capacity)} "
                )
            gr_logger.info(
                f"Congestion data generated into {output_file_name}.fig")

    @util.log_func
    def parse_input(self, input_file_path: str) -> list[Net]:
        """Parse the netlist input file

        Args:
            input_file_path (str): path of the netlist input file

        Returns:
            List[Net]: list of all nets
        """
        with open(input_file_path, "r", encoding="utf-8") as file:
            grid_data = file.readline().split()
            grid_horizontal_size = int(grid_data[1])
            grid_vertical_size = int(grid_data[2])
            vertical_capacity = int(file.readline().split()[2])
            horizontal_capacity = int(file.readline().split()[2])
            self.grid = Grid((grid_horizontal_size, grid_vertical_size),
                             (horizontal_capacity, vertical_capacity))
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
            gr_logger.info(
                f"{input_file_path} parsed successfully, data structures created")
            netlist_details = {
                "grid_hor": grid_horizontal_size,
                "grid_ver": grid_vertical_size,
                "ver_cap": vertical_capacity,
                "hor_cap": horizontal_capacity,
                "netlist_size": netlist_size
            }
            return netlist_details
