"""Module containing various methods for visualizing decomposition."""
from typing import Any, TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from decomposition import Decomposition


def init_axis():
    """Initializes figure object for plotting."""
    return plt.figure()


def display():
    """Display the figure."""
    plt.show()


def plot_decomposition(fig: Any, decomposition: 'Decomposition', order_num=1):
    """Function plots current status of decomposition.

    Args:
        fig (Any): Figure object from matplotlib that will be used to plot decomposition.
        decomposition (Decomposition): Instance of decomposition.
        order_num (int): Order of the subplot on the figure.
    """
    axis = fig.add_subplot(2, 1, order_num)
    plt.axis("equal")

    axis.get_yaxis().set_ticks([])
    axis.get_xaxis().set_ticks([])

    minx, miny, maxx, maxy = decomposition.orig_polygon.bounds

    for cell in decomposition.cells:
        axis.plot(*cell.exterior.xy, color='#6699cc', alpha=0.7,
                  linewidth=3, solid_capstyle='round', zorder=1)
        for hole in cell.interiors:
            axis.plot(*hole.xy, color='#6699cc', alpha=0.7,
                      linewidth=3, solid_capstyle='round', zorder=1)

    axis.set_xlim([minx - 0.5, maxx + 0.5])
    axis.set_ylim([miny - 0.5, maxy + 0.5])
