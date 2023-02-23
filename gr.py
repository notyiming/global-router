#!/usr/bin/env python3
"""Global Router Commands"""

import math
import click
from matplotlib import patches, pyplot as plt
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
    """Launch Global Router GUI
    \f

    Args:
        port (int, optional): Port number. Defaults to 5000.
        debug (bool, optional): Debug flag. Defaults to False.
    """
    app.run(port=port, debug=debug)


@gr_cli.command()
@click.option("-c", "--congestion_data_file_path", help="Congestion data file path", required=True)
@click.option("-p", "--plot_figure_filename", help="Plot figure filename", required=True)
@click.option("-d", "--display_plot_from_cli", is_flag=True, help="Display plot from CLI")
def plot_congestion(congestion_data_file_path: str, plot_figure_filename: str, display_plot_from_cli=False):
    """Plot congestion data visualization
    \f

    Args:
        congestion_data_file_path (str): Congestion data file path 
        plot_figure_filename (str): Plot figure filename
        display_plot (bool, optional): Display plot from CLI. Defaults to False.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 7.5))
    fig.set_facecolor("black")
    fig.tight_layout()
    with open(congestion_data_file_path, "r", encoding="utf-8") as data:
        grid_data = data.readline().split()
        grid_hor = int(grid_data[0])
        grid_ver = int(grid_data[1])
        num_hor = (grid_hor - 1)*grid_ver
        congestion_data = [float(n) for n in data.readline().split()]

        for i, congestion_level in enumerate(congestion_data):
            if congestion_level == 0:
                edge_color = "white"
            elif congestion_level <= 0.25:
                edge_color = "blue"
            elif congestion_level <= 0.5:
                edge_color = "cyan"
            elif congestion_level <= 0.75:
                edge_color = "green"
            elif congestion_level <= 1.0:
                edge_color = "yellow"
            else:
                edge_color = "red"

            if i < num_hor:
                x = 0.15 + int(i % (grid_hor-1))*0.6
                y = int(i/(grid_hor-1))*0.6
                ax.add_patch(patches.Rectangle(
                    (x, y),
                    0.4,
                    0.1,
                    edgecolor=edge_color,
                    facecolor=edge_color,
                    linestyle='-',
                ))
            else:
                x = int((i-num_hor) % (grid_hor))*0.6
                y = 0.15 + int((i-num_hor)/(grid_hor))*0.6
                ax.add_patch(patches.Rectangle(
                    (x, y),
                    0.1,
                    0.4,
                    edgecolor=edge_color,
                    facecolor=edge_color,
                    linestyle='-',
                ))
    ax.set_aspect('equal', adjustable='box')
    ax.set_frame_on(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    legend_elements = [
        patches.Patch(color="white", label="no use"),
        patches.Patch(color="blue", label="util <= 0.25"),
        patches.Patch(color="cyan", label="util <= 0.5"),
        patches.Patch(color="green", label="util <= 0.75"),
        patches.Patch(color="yellow", label="util <= 1.0"),
        patches.Patch(color="red", label="overflow")
    ]
    ax.legend(
        handles=legend_elements,
        title='Legend',
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        fontsize=8
    )

    ax.autoscale_view()
    plt.savefig(f"congestion_plots/{plot_figure_filename}", dpi=300)

    if display_plot_from_cli:
        plt.show()


if __name__ == "__main__":
    gr_cli()
