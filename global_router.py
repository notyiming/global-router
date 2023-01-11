#!/usr/bin/env python3
from components.GlobalRouter import GlobalRouter
import math
import sys


def main():
    global_router = GlobalRouter()
    if not len(sys.argv) == 3:
        print("Please provide input file and output file path")
        return
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    global_router.parse_input(input_file_path)
    global_router.show_netlist_info()

    best_route_index = 0
    best_route_overflow = math.inf
    best_wire_length = math.inf

    global_router.global_route()

    best_route_overflow = max(
        best_route_overflow, global_router.total_overflow)
    best_wire_length = max(best_wire_length, global_router.total_wire_length)

    if best_route_overflow > 0:
        global_router.rip_up_and_reroute()

    global_router.dump_result(output_file_path)
    global_router.generate_congestion_output(output_file_path)


if __name__ == "__main__":
    main()
