#!/usr/bin/env python3
"""Global Router Commands"""

import math
import click
from models.global_router import GlobalRouter
from web.app import app


@click.group()
def gr_cli():
    """Global Router Application"""


@gr_cli.command(short_help="Route the netlist")
@click.option("-i", "--input_file", help="Path to netlist input file", required=True)
@click.option("-o", "--output_file", help="Path to generated output file", required=True)
def global_route(input_file: str, output_file: str):
    """Global Route a netlist file and generate a routed output
    \f

    Args:
        input_file (str): Path to netlist input file
        output_file (str): Path to generated output file
    """
    global_router = GlobalRouter()
    global_router.parse_input(input_file)
    global_router.show_netlist_info()

    # best_route_index = 0
    best_route_overflow = math.inf
    best_wire_length = math.inf

    total_overflow, total_wirelength = global_router.global_route()

    best_route_overflow = min(best_route_overflow, total_overflow)
    best_wire_length = min(best_wire_length, total_wirelength)

    if best_route_overflow > 0:
        global_router.rip_up_and_reroute()

    global_router.dump_result(output_file)
    global_router.generate_congestion_output(output_file)

@gr_cli.command()
@click.option("-p", "--port", help="Port Selection", type=int)
@click.option("-d", "--debug", is_flag=True, help="Toggle debug mode")
def gui(port=5000, debug=False):
    """Launch Global Router GUI"""
    app.run(port=port, debug=debug)


if __name__ == "__main__":
    gr_cli()
