

# Global moduls
import os, sys, inspect
import math
from enum import Enum


# Local modules
subfolders = ["time_keeping", "decomposer", "sampler", "visuals", "gtsp", "cost_cal"]
for subfolder in subfolders:
	cmd_subfolder = os.path.realpath(
						os.path.abspath(
							os.path.join(
								os.path.split(
									inspect.getfile(
										inspect.currentframe()
									)
								)[0], subfolder
							)
						)
					)

	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)

import time_keeping as tk
import decomposer as dec
import line_samplers as lsmpl
import static_plotting as splot
import simple_cost as sc
import dubins_cost as dc
import gtsp

# Define Enum for methods
class Methods(Enum):
	map_grid_sampling = 0
	local_line_sampling_2dir = 1


def coverage_path_planner(map_poly, method, specs):
	"""
	Top function for coverage path planning.
	Accepts a map in the form of a sequence of points and bot specs.
	Return a coverage path.
	:param map_poly: A list of (x, y) tuples representing a map plus a list of holes
	:param method: Method to use for planning
	:param specs: Dict of specs of the bot
	:return path: Coverage path
	"""


	# Extract radius
	radius = specs["radius"]

	# Fire off the pipeline for particular method
	print("[%18s] Starting Coverage Path Planner."%tk.current_time())
	if method is Methods.local_line_sampling_2dir:
		print("[%18s] Using %s method."%(tk.current_time(), method))

		print("[%18s] Invoking greedy decomposition."%tk.current_time())
		cvx_set, connectivity, shared_edges = dec.greedy_decompose(map_poly)
		print("[%18s] Finished greedy decomposition."%tk.current_time())
		print cvx_set
		print connectivity
		print shared_edges
		print("[%18s] Startint to sample the free space with lines."%tk.current_time())
		lines = lsmpl.ilp_finite_dir_line_sampling(cvx_set, connectivity, shared_edges, [0, math.pi/2], specs)

		#print lines[0][0][0]
		#temp = lines[0][0][0]
		#lines[0][0][0] = lines[0][0][1]
		#lines[0][0][1] = temp
		#print lines[0][0][0]
		print("[%18s] Finished samling."%tk.current_time())

		print("[%18s] Initializing GTSP cost matrix."%tk.current_time())
		dict_mapping = lsmpl.init_dict_mapping(lines)

		print("[%18s] Computing the cost matrix."%tk.current_time())
		#cost_matrix, cluster_list = sc.init_cost_matrix(dict_mapping, lines)
		cost_matrix, cluster_list = dc.init_cost_matrix(dict_mapping, lines, specs)
		print("[%18s] Launching GTSP instance."%tk.current_time())
		gtsp.generate_gtsp_instance("cpp_test", "/home/sbochkar/misc/GLKH-1.0/", True, cost_matrix, cluster_list)

		print("[%18s] Reading the results."%tk.current_time())
		tour = gtsp.read_tour("cpp_test")
		tour = gtsp.process_tour(tour, cluster_list)
		ax = splot.init_axis()

		# Implementation missing for now
		# splot.plot_polygon_outline(ax, map_poly)

		print("[%18s] Plotting decomposition."%tk.current_time())
		splot.plot_decomposition(ax, cvx_set, shared_edges)

		print("[%18s] Plotting sampling."%tk.current_time())
		splot.plot_samples(ax, lines)

		print("[%18s] Plotting path."%tk.current_time())
		#splot.plot_tour(ax, tour, lines, dict_mapping)
		splot.plot_tour_dubins(ax, tour, lines, dict_mapping, radius)

		splot.display()
		
		
	elif method is Methods.map_grid_sampling:
		# Grid the map
		# Generate cost
		# Launch GTSP
		return


if __name__ == "__main__":

	specs = {"radius": 0.3}
	mappp = 1

	if mappp == 0:

		poly = [(5.0, 0),
				(10.0, 0),
				(10.0, 5.0),
				(15.0, 5.0),
				(15.0, 10.0),
				(10.0, 10.0),
				(10.0, 15.0),
				(5.0, 15.0),
				(5.0, 10.0),
				(0.0, 10.0),
				(0.0, 5.0),
				(5.0, 5.0)]

		holes = [[(6, 6),
				  (6, 9),
				  (9, 9),
				  (9, 6)]]
	elif mappp == 1:
		poly = [(0.0, 0),
				(5.0, 0),
				(5.0, 5.0),
				(0.0, 5.0)]
		holes = [[(1, 1),
				  (1, 4),
				  (4, 4),
				  (4, 1)]]

	elif mappp == 2:
		poly = [(0.0, 0),
				(15.0, 0),
				(15.0, 5.0),
				(10.0, 5.0),
				(10.0, 10.0),
				(5.0, 10.0),
				(5.0, 5.0),
				(0.0, 5.0)]
		holes = []		

	map_poly = [poly, holes]


	coverage_path_planner(map_poly, Methods.local_line_sampling_2dir, specs)