"""Single agent coverage planner."""
import sys

from pkg.poly_operations.hard_coded_lib import polygon_library
from pkg.decompositions import adjacency
from pkg.decompositions.greedy import greedy_decompose
#from pkg.decompositions.min_alt import min_alt_decompose
from pkg.discritizers.line import min_alt_discrt
#from pkg.discritizers.point import point_discrt
from pkg.discritizers import get_mapping
from pkg.costs import dubins_cost
from pkg.gtsp.GLKH import GTSPSolver
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
    def __init__(self, footprint_radius, dynamics):
        """Constructor.

        Args:
            footprint_radius (float): Radius of the coverage tool.
            dynamics (Any): Not used.
        """
        self.footprint_radius = footprint_radius
        self.footprint_diameter = 2 * footprint_radius
        self.dynamics = dynamics


def coverage_path_planner(polygon, robot, method):
    """
    Intry point for the single agent coverage path planning.

    Args:
        polygon (List): Polygon that will be decomposed.
        robot (Robot): Class containing "dynamics" of the robot.
        method (int): Which method to use.
    """
    decomposition = greedy_decompose.decompose(polygon)
    adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
    segments = min_alt_discrt.discritize_set(decomposition, robot.footprint_diameter)
    mapping = get_mapping.get_mapping(segments)
    cost_matrix, cluster_list = dubins_cost.compute_costs(
        polygon, mapping, robot.footprint_radius)

    solver = GTSPSolver("cpp_test", cost_matrix, cluster_list)
    tour = solver.launch_solver_and_get_tour()

    return decomposition, adjacency_matrix, segments, tour, mapping

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
#        cost_matrix, cluster_list = dubins_cost.compute_costs(polygon, mapping, robot.footprint_diameter/2)
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
#        splot.plot_tour_dubins(ax, tour, mapping, robot.footprint_radius)
#
#        logger.info("Tour Length %2f.")
#
#        splot.display()
#
#    elif method == 2:
#
#        logger.info("Populating the free space with segments.")
#        segments = point_discrt.discritize_polygon(polygon, robot.footprint_radius)
#        logger.info("Finished generating segments.")
#
#        logger.info("Obtain a mapping between nodes and segments.")
#        mapping = get_mapping.get_mapping(segments)
#        logger.info("Obtained mapping.")
#
#        logger.info("Started computing the cost matrix.")
##		cost_matrix, cluster_list = dubins_cost.compute_costs(polygon, mapping, robot.footprint_radius)
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
#        splot.plot_tour_dubins(ax, tour, mapping, robot.footprint_radius)
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
#        segments = min_alt_discrt.discritize_set(decomposition, robot.footprint_diameter)
#        logger.info("Finished generating segments.")
#
#        logger.info("Obtain a mapping between nodes and segments.")
#        mapping = get_mapping.get_mapping(segments)
#        logger.info("Obtained mapping.")
#
#        logger.info("Started computing the cost matrix.")
#        cost_matrix, cluster_list = dubins_cost.compute_costs(P, mapping, robot.footprint_radius)
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
#        splot.plot_tour_dubins(ax, tour, mapping, robot.footprint_radius)
#
#        logger.info("Tour Length %2f.")
#        splot.display()
#        logger.info("polygonolygon Area: %2f")
#        logger.info("Area covered: %2f")
#
#    elif method == 4:
#        logger.info("Populating the free space with segments.")
#        segments = point_discrt.discritize_polygon(polygon, robot.footprint_radius)
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
#        splot.plot_tour_dubins(ax, tour, mapping, robot.footprint_radius)
#
#        #logger.info("Tour Length %2f.")
#
#        splot.display()

if __name__ == "__main__":

    # Generating a polygon
    logger.info("Generating a polygon.")
    polygon = polygon_library.polygon_generator(int(sys.argv[1]))
    logger.info("Polygon generated.")

    robot = Robot(0.2, "dubins")
    
    decomposition, adjacency_matrix, segments, tour, mapping = coverage_path_planner(polygon, robot, 0)

    ax = splot.init_axis()
    splot.plot_decomposition(ax, decomposition, adjacency_matrix, polygon)
    splot.plot_samples(ax, segments)
    splot.plot_tour_dubins(ax, tour, mapping, robot.footprint_radius)
    splot.display()

