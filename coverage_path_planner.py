#Local modules
from pkg.time_keeping import time_keeping as tk
from pkg.poly_operations.hard_coded_lib import polygon_library
from pkg.decompositions import adjacency
from pkg.decompositions.greedy import greedy_decompose
#from pkg.decompositions.min_alt import min_alt_decompose
from pkg.discritizers.line import min_alt_discrt
#from pkg.discritizers.point import point_discrt
from pkg.discritizers import get_mapping
from pkg.costs import dubins_cost
from pkg.gtsp.GLKH import solver
from pkg.visuals.static	import coverage_plot as splot
#from pkg.analysis import tour_length
#from pkg.analysis import tour_area
#from pkg.poly_operations.others	import operations

from log_utils import get_logger


# pylint: disable=invalid-name
logger = get_logger("main")
# pylint: enable=invalid-name


class Robot:
    """
    Container class with robot "dynamics".
    """
    def __init__(self, footprint_width, dynamics):
        self.footprint_width = footprint_width
        self.dynamics = dynamics


def coverage_path_planner(polygon, robot, method):
    """
    Intry point for the single agent coverage path planning.

    Args:
        polygon (List): Polygon that will be decomposed.
        robot (Robot): Class containing "dynamics" of the robot.
        method (int): Which method to use.
    """
    # TODO: Out of place.
    width = 2 * robot.footprint_width

    if method == 0: # Greed convex decomposion method

        logger.info("Invoking greedy decomposition.")
        decomposition = greedy_decompose.decompose(polygon)
        logger.info("Finished greedy decomposition.")

        logger.info("Forming an adjacency matrix for polygons.")
        adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
        logger.info("Adjacency matrix complete.")

        logger.info("Populating the free space with segments.")
        segments = min_alt_discrt.discritize_set(decomposition, width)
        logger.info("Finished generating segments.")

        logger.info("Obtain a mapping between nodes and segments.")
        mapping = get_mapping.get_mapping(segments)
        logger.info("Obtained mapping.")

        logger.info("Started computing the cost matrix.")
        cost_matrix, cluster_list = dubins_cost.compute_costs(polygon, mapping, width/2)
        logger.info("Finished computing the cost matrix.")

        logger.info("Generating and launching GTSP instance.")
        solver.solve("cpp_test", cost_matrix, cluster_list)
        logger.info("Sovled GTSP instance.")

        logger.info("Reading the results.")
        tour = solver.read_tour("cpp_test")

        logger.info("Plotting the results.")
        ax = splot.init_axis()

        logger.info("Plotting decomposition.")
        splot.plot_decomposition(ax, decomposition, adjacency_matrix, polygon)

        logger.info("Plotting sampling.")
        splot.plot_samples(ax, segments)

        logger.info("Plotting path.")
        #splot.plot_tour(ax, tour, lines, dict_mapping)
        splot.plot_tour_dubins(ax, tour, mapping, width/2)

        logger.info("Tour Length %2f.")
        logger.info("polygonolygon Area: %2f")
        logger.info("Area covered: %2f")
        splot.display()

#    elif method == 1:
#        logger.info("Invoking min_alt decomposition.")
#        decomposition = min_alt_decompose.decompose(polygon)
#        logger.info("Finished min_alt decomposition.")
#    #	print decomposition
#
#        logger.info("Forming an adjacency matrix for polygons.")
#        adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
#        logger.info("Adjacency matrix complete.")
#
#        logger.info("Populating the free space with segments.")
#        segments = min_alt_discrt.discritize_set(decomposition, width)
#        logger.info("Finished generating segments.")
#
#        logger.info("Obtain a mapping between nodes and segments.")
#        mapping = get_mapping.get_mapping(segments)
#        logger.info("Obtained mapping.")
#
#        logger.info("Started computing the cost matrix.")
#        cost_matrix, cluster_list = dubins_cost.compute_costs(polygon, mapping, width/2)
#        logger.info("Finished computing the cost matrix.")
#
#        logger.info("Generating and launching GTSP instance.")
#        solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
#        logger.info("Sovled GTSP instance.")
#
#        logger.info("Reading the results.")
#        tour = solver.read_tour("cpp_test")
#
#        logger.info("Plotting the results.")
#        ax = splot.init_axis()
#
#        logger.info("Plotting decomposition.")
#        splot.plot_decomposition(ax, decomposition, adjacency_matrix)
#
#        logger.info("Plotting sampling.")
#        splot.plot_samples(ax, segments)
#
#        logger.info("Plotting path.")
#        #splot.plot_tour(ax, tour, lines, dict_mapping)
#        splot.plot_tour_dubins(ax, tour, mapping, width/2)
#
#        logger.info("Tour Length %2f.")
#
#        splot.display()
#
#    elif method == 2:
#
#        logger.info("Populating the free space with segments.")
#        segments = point_discrt.discritize_polygon(polygon, width/2)
#        logger.info("Finished generating segments.")
#
#        logger.info("Obtain a mapping between nodes and segments.")
#        mapping = get_mapping.get_mapping(segments)
#        logger.info("Obtained mapping.")
#
#        logger.info("Started computing the cost matrix.")
##		cost_matrix, cluster_list = dubins_cost.compute_costs(polygon, mapping, width/2)
#        logger.info("Finished computing the cost matrix.")
#
#        logger.info("Generating and launching GTSP instance.")
##		solver.solve("gtsp_13_coverage", GLKH_LOCATION, cost_matrix, cluster_list)
#        logger.info("Sovled GTSP instance.")
#
#
#        logger.info("Reading the results.")
#        tour = solver.read_tour("gtsp_13_coverage")
#
#
#        logger.info("Plotting the results.")
#        ax = splot.init_axis()
#
#        logger.info("Plotting decomposition.")
#        splot.plot_polygon_outline(ax, polygon)
#
#        logger.info("Plotting sampling.")
#        splot.plot_samples(ax, segments)
#
#        logger.info("Plotting path.")
#        #splot.plot_tour(ax, tour, lines, dict_mapping)
#        splot.plot_tour_dubins(ax, tour, mapping, width/2)
#
##		logger.info("Tour Length %2f.")
#        splot.display()
#        logger.info("polygonolygon Area: %2f")
#        logger.info("Area covered: %2f")
#
#    elif method == 3:
#        logger.info("Invoking min_alt decomposition.")
##		decomposition = [
##			[[(0.0,  0.0), (10.0,  0.0),(1.0, 1.0)],[]],
##			[[(1.0,  1.0), (10.0,  0.0),(9.0, 1.0)],[]],
##			[[(10.0, 0.0), (10.0, 10.0),(9.0, 9.0)],[]],
##			[[(10.0, 0.0), (9.0, 9.0),(9.0, 1.0)],[]],
##			[[(10.0, 10.0),(9.0, 9.0),(1.0, 9.0)],[]],
##			[[(1.0, 9.0), (0.0, 10.0),(10.0, 10.0)],[]],
##			[[(0.0,  0.0), (1.0, 1.0),(0.0, 10.0)], []],
##			[[(0.0,  10.0), (1.0, 1.0),(1.0, 9.0)], []]
##		]
#        decomposition = greedy_decompose.decompose(polygon)
#        logger.info("Finished min_alt decomposition.")
#
#
#        logger.info("Forming an adjacency matrix for polygons.")
#        adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
#        logger.info("Adjacency matrix complete.")
#
#
#        logger.info("Forming an adjacency matrix for polygons.")
#        decomposition = min_alt_decompose.reoptimize(polygon, decomposition, adjacency_matrix)
#        logger.info("Adjacency matrix complete.")
#
#        logger.info("Forming an adjacency matrix for polygons.")
#        adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
#        logger.info("Adjacency matrix complete.")
#
#
#        logger.info("Populating the free space with segments.")
#        segments = min_alt_discrt.discritize_set(decomposition, width)
#        logger.info("Finished generating segments.")
#
#        logger.info("Obtain a mapping between nodes and segments.")
#        mapping = get_mapping.get_mapping(segments)
#        logger.info("Obtained mapping.")
#
#        logger.info("Started computing the cost matrix.")
#        cost_matrix, cluster_list = dubins_cost.compute_costs(P, mapping, width/2)
#        logger.info("Finished computing the cost matrix.")
#
#        logger.info("Generating and launching GTSpolygon instance.")
#        solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
#        logger.info("Sovled GTSP instance.")
#
#
#        logger.info("Reading the results.")
#        tour = solver.read_tour("cpp_test")
#
#
#        logger.info("Plotting the results.")
#        ax = splot.init_axis()
#        logger.info("Plotting decomposition.")
#        splot.plot_decomposition(ax, decomposition, adjacency_matrix, polygon)
##		splot.display()
#
#        logger.info("Plotting sampling.")
#        splot.plot_samples(ax, segments)
#
#        logger.info("Plotting path.")
#        #splot.plot_tour(ax, tour, lines, dict_mapping)
#        splot.plot_tour_dubins(ax, tour, mapping, width/2)
#
#        logger.info("Tour Length %2f.")
#        splot.display()
#        logger.info("polygonolygon Area: %2f")
#        logger.info("Area covered: %2f")
#
#    elif method == 4:
#        logger.info("Populating the free space with segments.")
#        segments = point_discrt.discritize_polygon(polygon, width/2)
#        logger.info("Finished generating segments.")
#
#        logger.info("Obtain a mapping between nodes and segments.")
#        mapping = get_mapping.get_mapping(segments)
#        logger.info("Obtained mapping.")
#
#        logger.info("Reading the results.")
#        tour = solver.read_tour("cpp_test")
#
#        logger.info("Plotting the results.")
#        ax = splot.init_axis()
#
#        logger.info("Plotting decomposition.")
#        splot.plot_polygon_outline(ax, polygon)
#
#        logger.info("Plotting sampling.")
#        splot.plot_samples(ax, segments)
#
#        logger.info("Plotting path.")
#        #splot.plot_tour(ax, tour, lines, dict_mapping)
#        splot.plot_tour_dubins(ax, tour, mapping, width/2)
#
#        #logger.info("Tour Length %2f.")
#
#        splot.display()

if __name__ == "__main__":

    # Generating a polygon
    logger.info("Generating a polygon.")
    polygon = polygon_library.polygon_generator(1)
    logger.info("Polygon generated.")

    robot = Robot(0.2, "dubins")
    coverage_path_planner(polygon, robot, 0)
