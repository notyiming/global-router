#!/usr/bin/env python3
"""Global Router Commands"""

import copy
import math
import multiprocessing
from typing import Dict, Tuple
import rich_click as click
from matplotlib import patches, pyplot as plt
import numpy as np
import mpld3
from models.global_router import GlobalRouter
from logs.gr_logger import gr_logger
import web.app as flask_app
from rich.live import Live
from rich.table import Table
from rich.console import Console
from constants import banner


@click.group()
def gr_cli():
    """Global Router Application"""

@gr_cli.command(short_help="Route the netlist")
@click.argument("input_file")
@click.argument("output_file")
@click.option("-a", "--algorithm", default=1, help="1. Best First Search 2. Breadth First Search", type=int)
@click.option("-s", "--seed", default=-1, help="Random seed", type=int)
def global_route(input_file: str, output_file: str, algorithm: int, seed: int | None) -> Tuple[Dict, GlobalRouter]:
    """Global Route a netlist file and generate a routed output
    \f

    Args:
        input_file (str): Path to netlist input file
        output_file (str): Path to generated output file
        algorithm (int, optional): Routing algorithm. Defaults to 1.
        seed (int, optional): Random seed. Defaults to None.
    """
    console = Console()
    console.print(banner, style="blue")
    global_router = GlobalRouter(algorithm, seed)
    netlist_details = global_router.parse_input(input_file)
    table = Table(title="Layout and Netlist Details")
    cols = [
        ("Grid", {}),
        ("Vertical Capacity", dict(style="green")),
        ("Horizontal Capacity", dict(style="green")),
        ("Number of nets", dict(style="blue"))
    ]
    for col, style in cols:
        table.add_column(col, **style)
    table.add_row(
        f"{netlist_details['grid_hor']} x {netlist_details['grid_ver']}",
        f"{netlist_details['ver_cap']}",
        f"{netlist_details['hor_cap']}",
        f"{netlist_details['netlist_size']}"
        )
    console.print(table)

    if seed and seed != -1:
        gr_logger.info(f"Seed detected: {seed}")
        num_threads = 1
    else:
        num_threads = 5

    if algorithm == 2:
        num_threads = 1


    global_routers: list[GlobalRouter] = []
    for _ in range(num_threads):
        router_copy = copy.deepcopy(global_router)
        global_routers.append(router_copy)

    best_gr_index = 0
    min_overflow = math.inf
    min_wirelength = math.inf

    gr_logger.info(f"Number of Global Routers in parallel: {num_threads}")


    with Live(_generate_table(), auto_refresh=False) as live:
        global_routers: list[GlobalRouter] = []
        for _ in range(num_threads):
            router_copy = copy.deepcopy(global_router)
            global_routers.append(router_copy)
        # create more global routers, pick the best result
        with multiprocessing.Pool(num_threads) as p:
            global_routers = p.map(_run_global_route, global_routers)

        gr_results = []
        for i in range(num_threads):
            router = global_routers[i]
            if router.overflow < min_overflow or (router.overflow == min_overflow and router.wirelength < min_wirelength):
                min_overflow = router.overflow
                min_wirelength = router.wirelength
                best_gr_index = i
            gr_results.append(dict(
                id=i+1,
                best_overflow=router.overflow,
                best_wirelength=router.wirelength
            ))
            live.update(_generate_table(gr_results))

    initial_res_table = Table(title="Initial Routing Result")
    cols = [
        ("Best Router Index", {}),
        ("Best Router Seed", {}),
        ("Best Overflow", dict(style="red")),
        ("Best Wirelength", dict(style="blue"))
    ]
    for col, style in cols:
        initial_res_table.add_column(col, **style)
    initial_res_table.add_row(
        f"{best_gr_index}",
        f"{global_routers[best_gr_index].seed}",
        f"{min_overflow}",
        f"{min_wirelength}"
        )
    console.print(initial_res_table)


    num_of_reroutes_attempts = 0 if algorithm == 2 else 10

    if min_overflow > 0:
        num_of_reroutes = 0
        while num_of_reroutes < num_of_reroutes_attempts and min_overflow > 0:
            gr_logger.debug(f"Rip-up and reroute #{num_of_reroutes + 1}:")
            new_min_overflow, new_min_wirelength = global_routers[best_gr_index].rip_up_and_reroute(
            )
            if new_min_overflow < min_overflow or (new_min_overflow == min_overflow and new_min_wirelength < min_wirelength):
                min_overflow = new_min_overflow
                min_wirelength = new_min_wirelength
            gr_logger.debug(f"New Min Overflow: {new_min_overflow}")
            gr_logger.debug(f"New Min Wirelength: {new_min_wirelength}")
            num_of_reroutes += 1

    final_res_table = Table(title="Final Routing Result")
    cols = [
        ("Best Router Index", {}),
        ("Best Router Seed", {}),
        ("Best Overflow", dict(style="red")),
        ("Best Wirelength", dict(style="blue"))
    ]
    for col, style in cols:
        final_res_table.add_column(col, **style)
    final_res_table.add_row(
        f"{best_gr_index}",
        f"{global_routers[best_gr_index].seed}",
        f"{min_overflow}",
        f"{min_wirelength}"
        )
    console.print(final_res_table)

    global_routers[best_gr_index].dump_result(output_file)
    global_routers[best_gr_index].generate_congestion_output(output_file)
    return (netlist_details, global_routers[best_gr_index])

def _generate_table(gr_results=None) -> Table:
    gr_table = Table(title="Global Routers in Parallel")
    cols = [
        ("Global Router ID", {}),
        ("Total Overflow", dict(style="red")),
        ("Total Wirelength", dict(style="blue"))
    ]
    for col, style in cols:
        gr_table.add_column(col, **style)
    if gr_results is not None:
        for res in gr_results:
            gr_table.add_row(
                f"{res['id']}",
                f"{res['best_overflow']}",
                f"{res['best_wirelength']}"
            )
    return gr_table

def _run_global_route(router: GlobalRouter):
    router.route()
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
        congestion_data = np.array([float(n) for n in data.readline().split()])

        # Get the corresponding colors for each congestion level
        colors = np.select(
            [congestion_data == 0, congestion_data <= 0.25, congestion_data <= 0.5,
             congestion_data <= 0.75, congestion_data <= 1.0, congestion_data > 1.0],
            ["white", "blue", "cyan", "green", "yellow", "red"]
        )

        # Calculate the x and y coordinates for each rectangle
        x = np.concatenate([
            np.array([0.15 + int(i % (grid_hor-1))
                     * 0.6 for i in range(num_hor)]),
            np.array([int((i-num_hor) % (grid_hor)) *
                     0.6 for i in range(num_hor, len(congestion_data))])
        ])
        y = np.concatenate([
            np.array([int(i/(grid_hor-1))*0.6 for i in range(num_hor)]),
            np.array([0.15 + int((i-num_hor)/(grid_hor)) *
                     0.6 for i in range(num_hor, len(congestion_data))])
        ])

        # Plot the rectangles
        with click.progressbar(range(len(congestion_data)), label="Generating Congestion Plot") as data:
            for i in data:
                ax.add_patch(patches.Rectangle(
                    (x[i], y[i]),
                    0.4 if i < num_hor else 0.1,
                    0.1 if i < num_hor else 0.4,
                    edgecolor=colors[i],
                    facecolor=colors[i],
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
