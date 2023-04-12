#!/usr/bin/env python3
"""Global Router Commands"""

import copy
import math
import click
import multiprocessing
from matplotlib import patches, pyplot as plt
import mpld3
from models.global_router import GlobalRouter
from logs.gr_logger import gr_logger
import web.app as flask_app


@click.group()
def gr_cli():
    """Global Router Application"""


@gr_cli.command(short_help="Route the netlist")
@click.argument("input_file")
@click.argument("output_file")
def global_route(input_file: str, output_file: str):
    """Global Route a netlist file and generate a routed output
    \f

    Args:
        input_file (str): Path to netlist input file
        output_file (str): Path to generated output file
    """
    global_router = GlobalRouter()
    netlist_details = global_router.parse_input(input_file)
    global_router.show_netlist_info()

    # num_threads = 5
    # global_routers: list[GlobalRouter] = []
    # for _ in range(num_threads):
    #     router_copy = copy.deepcopy(global_router)
    #     global_routers.append(router_copy)

    # best_gr_index = 0
    # min_overflow = math.inf
    # min_wirelength = math.inf

    # gr_logger.info(f"Number of Global Routers in parallel: {num_threads}")

    # # create more global routers, pick the best result
    # with multiprocessing.Pool(num_threads) as p:
    #     global_routers = p.map(_run_global_route, global_routers)

    # for i in range(num_threads):
    #     router = global_routers[i]
    #     if router.overflow < min_overflow or (router.overflow == min_overflow and router.wirelength < min_wirelength):
    #         min_overflow = router.overflow
    #         min_wirelength = router.wirelength
    #         best_gr_index = i
    global_router.global_route()
    # gr_logger.info(
    #     "\n==============================\n"
    #     "    Initial Routing Result    \n"
    #     "==============================\n"
    #     f"Best Router Index: {best_gr_index}\n"
    #     f"Best Overflow: {min_overflow}\n"
    #     f"Best Wirelength: {min_wirelength}\n"
    #     "==============================\n")

    # if min_overflow > 0:
    #     num_of_reroutes = 0
    #     while num_of_reroutes < 10 and min_overflow > 0:
    #         gr_logger.info(f"Rip-up and reroute #{num_of_reroutes + 1}:")
    #         # new_min_overflow, new_min_wirelength = global_routers[best_gr_index].rip_up_and_reroute()
    #         new_min_overflow, new_min_wirelength = global_router.rip_up_and_reroute()
    #         if new_min_overflow < min_overflow or (new_min_overflow == min_overflow and new_min_wirelength < min_wirelength):
    #             min_overflow = new_min_overflow
    #             min_wirelength = new_min_wirelength
    #         gr_logger.info(f"New Min Overflow: {new_min_overflow}")
    #         gr_logger.info(f"New Min Wirelength: {new_min_wirelength}")
    #         num_of_reroutes += 1

    min_overflow = global_router.overflow
    min_wirelength = global_router.wirelength
    if min_overflow > 0:
        num_of_reroutes = 0
        while num_of_reroutes < 10 and min_overflow > 0:
            gr_logger.info(f"Rip-up and reroute #{num_of_reroutes + 1}:")
            # new_min_overflow, new_min_wirelength = global_routers[best_gr_index].rip_up_and_reroute()
            new_min_overflow, new_min_wirelength = global_router.rip_up_and_reroute()
            if new_min_overflow < min_overflow or (new_min_overflow == min_overflow and new_min_wirelength < min_wirelength):
                min_overflow = new_min_overflow
                min_wirelength = new_min_wirelength
            gr_logger.info(f"New Min Overflow: {new_min_overflow}")
            gr_logger.info(f"New Min Wirelength: {new_min_wirelength}")
            num_of_reroutes += 1

    # gr_logger.info(
    #     "\n==============================\n"
    #     "     Final Routing Result     \n"
    #     "==============================\n"
    #     f"Best Router Index: {best_gr_index}\n"
    #     f"Best Overflow: {min_overflow}\n"
    #     f"Best Wirelength: {min_wirelength}\n"
    #     "==============================\n")

    # global_routers[best_gr_index].dump_result(output_file)
    # global_routers[best_gr_index].generate_congestion_output(output_file)
    global_router.dump_result(output_file)
    global_router.generate_congestion_output(output_file)
    # return (netlist_details, min_overflow, min_wirelength)
    return (netlist_details, global_router.overflow, global_router.wirelength)


def _run_global_route(router: GlobalRouter):
    router.global_route()
    return router


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
    flask_app.app.run(port=port, debug=debug)


@gr_cli.command()
@click.argument("congestion_data_file_path")
@click.option("-d", "--display_plot_from_cli", is_flag=True, help="Display plot from CLI")
def plot_congestion(congestion_data_file_path: str, display_plot_from_cli=False) -> str:
    """Plot congestion data visualization
    \f

    Args:
        congestion_data_file_path (str): Congestion data file path 
        display_plot (bool, optional): Display plot from CLI. Defaults to False.

    Returns:
        str: plot figure html
    """
    fig, ax = plt.subplots()
    ax.set_facecolor("black")
    fig.tight_layout()
    plt.xticks([])
    plt.yticks([])
    with open(congestion_data_file_path, "r", encoding="utf-8") as data:
        grid_data = data.readline().split()
        grid_hor = int(grid_data[0])
        grid_ver = int(grid_data[1])
        num_hor = (grid_hor - 1)*grid_ver
        congestion_data = [float(n) for n in data.readline().split()]

        with click.progressbar(congestion_data, label="Generating Congestion Plot") as congestion_data:
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
    ax.autoscale_view()

    if display_plot_from_cli:
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
        )
        plt.show()

    return mpld3.fig_to_html(fig, no_extras=True)


if __name__ == "__main__":
    gr_cli()
