""" Main entypoint for coverage path planning."""
import sys

from decomposition.decomposition import Decomposition
from polygons.polygons import polygon_factory
from optimizer.min_alt_optimizer import min_alt_optimize, vertex_sampler
from visuals.coverage_plot import plot_decomposition


def main(polygon_id: int):
    """ Main entrypoint for the CPP."""

    decomposition = Decomposition(polygon_factory(polygon_id))
    samples = vertex_sampler(decomposition)
    min_alt_optimize(decomposition, samples)
    plot_decomposition(decomposition)


if __name__ == "__main__":
    main(int(sys.argv[1]))
