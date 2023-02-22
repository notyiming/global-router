#!/usr/bin/env python3
"""Global Router Commands"""

import math
import click
from matplotlib import patches, pyplot as plt
from matplotlib.lines import Line2D
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
@click.option("-c", "--congestion_data_file_path", help="Congestion Data File Path", required=True)
@click.option("-d", "--display_plot", is_flag=True, help="Display plot")
def plot_congestion(congestion_data_file_path: str, display_plot=False):
    """Plot congestion data visualization
    \f

    Args:
        congestion_data_file_path (str): Congestion data
    """
    COLOR = ['white', 'blue', 'cyan', 'green', 'yellow', 'red']
    fig = plt.figure()
    ax = fig.add_subplot()
    with open(congestion_data_file_path, "r", encoding="utf-8") as data:
        grid_data = data.readline().split()
        grid_hor = int(grid_data[0])
        grid_ver = int(grid_data[1])
        num_hor = (grid_hor - 1)*grid_ver
        congestion_data = [float(n) for n in data.readline().split()]
        ax.add_patch(
            patches.Rectangle(
                (0, 0),
                0.6*grid_hor - 0.5 + 2,
                0.6*grid_ver - 0.5 + 2,
                alpha=1, facecolor='black', edgecolor='black', linestyle='-', fill=True
            )
        )
        ax.add_patch(
            patches.Rectangle(
                (0.6*grid_hor - 0.5 + 2, 0),
                0.2*grid_ver - 0.5 + 2,
                0.6*grid_ver - 0.5 + 2,
                alpha=1, facecolor='black', edgecolor='black', linestyle='-', fill=True
            )
        )
        for i, congestion_level in enumerate(congestion_data):
            if congestion_level == 0:
                edge_color = COLOR[0]
            elif congestion_level <= 0.25:
                edge_color = COLOR[1]
            elif congestion_level <= 0.5:
                edge_color = COLOR[2]
            elif congestion_level <= 0.75:
                edge_color = COLOR[3]
            elif congestion_level <= 1.0:
                edge_color = COLOR[4]
            else:
                edge_color = COLOR[5]

            if i < num_hor:
                x = 1 + 0.14 + int(i % (grid_hor-1))*0.6
                y = 1 + int(i/(grid_hor-1))*0.6
                ax.add_patch(
                    patches.Rectangle(
                        (x, y),
                        0.4,
                        0.1,
                        facecolor=edge_color,
                        edgecolor=edge_color,
                        linestyle='-',
                    )
                )
            else:
                x = 1 + int((i-num_hor) % (grid_hor))*0.6
                y = 1 + 0.14 + int((i-num_hor)/(grid_hor))*0.6
                ax.add_patch(
                    patches.Rectangle(
                        (x, y),
                        0.1,
                        0.4,
                        facecolor=edge_color,
                        edgecolor=edge_color,
                        linestyle='-',
                    )
                )
    legend_elements = [Line2D([0], [0], color=COLOR[0], lw=4, label='no use'),
                       Line2D([0], [0], color=COLOR[1],
                              lw=4, label='util <= 0.25'),
                       Line2D([0], [0], color=COLOR[2],
                              lw=4, label='util <= 0.5'),
                       Line2D([0], [0], color=COLOR[3],
                              lw=4, label='util <= 0.75'),
                       Line2D([0], [0], color=COLOR[4],
                              lw=4, label='util <= 1.0'),
                       Line2D([0], [0], color=COLOR[5], lw=4, label='overflow')]
    plt.legend(handles=legend_elements, loc='lower right', title='Legend')

    ax.autoscale_view()
    plt.savefig("congestion_plots/ming.png", dpi=300)

    if display_plot:
        plt.show()


if __name__ == "__main__":
    gr_cli()
