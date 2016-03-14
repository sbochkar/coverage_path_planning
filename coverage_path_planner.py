

#Global imports
import math
from enum import Enum
from shapely.geometry import LineString

#Local modules
from pkg.time_keeping					import time_keeping as tk
from pkg.poly_operations.hard_coded_lib import polygon_library
from pkg.poly_operations.others			import adjacency
from pkg.decompositions.greedy 			import greedy_decompose
from pkg.decompositions.min_alt			import min_alt_decompose
from pkg.discritizers.line 				import min_alt_discrt
from pkg.discritizers	 				import get_mapping
from pkg.costs							import dubins_cost
from pkg.gtsp.GLKH						import solver
from pkg.visuals.static					import coverage_plot as splot


class Robot:
	"""
	Robot class cotaining specs
	"""
	def __init__(self, footprint_width, dynamics):
		self.footprint_width = footprint_width
		self.dynamics = dynamics


GLKH_LOCATION = "/home/stan/misc/GLKH-1.0/"


def coverage_path_planner(map_num, robot, method):
	"""
	Wrapper for all avaialble path planners

	:param map_num: Id of a map
	:param method: Method to use for planning
	:param robot: RObot specs
	:return path: Coverage path
	"""


	# Generating a polygon
	print("[%18s] Generating a polygon."%tk.current_time())
	P = polygon_library.polygon_generator(map_num)
	print("[%18s] Polygon generated."%tk.current_time())
	
	width = 2*robot.footprint_width

	if method == 0: # Greed convex decomposion method

		print("[%18s] Invoking greedy decomposition."%tk.current_time())
		decomposition = greedy_decompose.decompose(P)
		print("[%18s] Finished greedy decomposition."%tk.current_time())

		print("[%18s] Forming an adjacency matrix for polygons."%tk.current_time())
		adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
		print("[%18s] Adjacency matrix complete."%tk.current_time())

		print("[%18s] Populating the free space with segments."%tk.current_time())
		segments = min_alt_discrt.discritize_set(decomposition, width)
		print("[%18s] Finished generating segments."%tk.current_time())

		print("[%18s] Obtain a mapping between nodes and segments."%tk.current_time())
		mapping = get_mapping.get_mapping(segments)
		print("[%18s] Obtained mapping."%tk.current_time())

		print("[%18s] Started computing the cost matrix."%tk.current_time())
		cost_matrix, cluster_list = dubins_cost.compute_costs(mapping, width/2)
		print("[%18s] Finished computing the cost matrix."%tk.current_time())

		print("[%18s] Generating and launching GTSP instance."%tk.current_time())
		solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
		print("[%18s] Sovled GTSP instance."%tk.current_time())


		print("[%18s] Reading the results."%tk.current_time())
		tour = solver.read_tour("cpp_test")

		print("[%18s] Plotting the results."%tk.current_time())		
		ax = splot.init_axis()

		print("[%18s] Plotting decomposition."%tk.current_time())
		splot.plot_decomposition(ax, decomposition, adjacency_matrix)

		print("[%18s] Plotting sampling."%tk.current_time())
		splot.plot_samples(ax, segments)

		print("[%18s] Plotting path."%tk.current_time())
		#splot.plot_tour(ax, tour, lines, dict_mapping)
		splot.plot_tour_dubins(ax, tour, mapping, width/2)

		splot.display()

	elif method == 1:
		print("[%18s] Invoking min_alt decomposition."%tk.current_time())
		decomposition = min_alt_decompose.decompose(P)
		print("[%18s] Finished min_alt decomposition."%tk.current_time())
	#	print decomposition

		print("[%18s] Forming an adjacency matrix for polygons."%tk.current_time())
		adjacency_matrix = adjacency.get_adjacency_as_matrix(decomposition)
		print("[%18s] Adjacency matrix complete."%tk.current_time())

		print("[%18s] Populating the free space with segments."%tk.current_time())
		segments = min_alt_discrt.discritize_set(decomposition, width)
		print("[%18s] Finished generating segments."%tk.current_time())

		print("[%18s] Obtain a mapping between nodes and segments."%tk.current_time())
		mapping = get_mapping.get_mapping(segments)
		print("[%18s] Obtained mapping."%tk.current_time())

		print("[%18s] Started computing the cost matrix."%tk.current_time())
		cost_matrix, cluster_list = dubins_cost.compute_costs(P, mapping, width/2)
		print("[%18s] Finished computing the cost matrix."%tk.current_time())

		print("[%18s] Generating and launching GTSP instance."%tk.current_time())
		solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
		print("[%18s] Sovled GTSP instance."%tk.current_time())


		print("[%18s] Reading the results."%tk.current_time())
		tour = solver.read_tour("cpp_test")

		print("[%18s] Plotting the results."%tk.current_time())		
		ax = splot.init_axis()

		print("[%18s] Plotting decomposition."%tk.current_time())
		splot.plot_decomposition(ax, decomposition, adjacency_matrix)

		print("[%18s] Plotting sampling."%tk.current_time())
		splot.plot_samples(ax, segments)

		print("[%18s] Plotting path."%tk.current_time())
		#splot.plot_tour(ax, tour, lines, dict_mapping)
		splot.plot_tour_dubins(ax, tour, mapping, width/2)

		splot.display()





if __name__ == "__main__":

	robot = Robot(0.2, "dubins")
	coverage_path_planner(7, robot, 1)