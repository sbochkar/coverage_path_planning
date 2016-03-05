

# Global moduls
import os, sys, inspect
import math
from enum import Enum
from shapely.geometry import LineString

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
import point_sampler as psmpl
import static_plotting as splot
import simple_cost as sc
import dubins_cost as dc
import gtsp

# Define Enum for methods
class Methods(Enum):
	grid_gtsp = 0
	local_line_sampling_2dir = 1
	greedy_decomp = 2
	min_alt_decomp = 3


def output_path_stats(line_list, tour, cost_matrix):
	"""
	Function will print info about the path
	"""

	# First sum up the lengths of the lines
	tour_length = 0
	for line_set in line_list:
		for line in line_set:
			ls_line = LineString(line)
			tour_length += ls_line.length

	# Now compute the cost of the transitions
	for i in range(len(tour)-1):
		o_node = tour[i]
		i_node = tour[i+1]

		tour_length += cost_matrix[o_node][i_node]

	tour_length += cost_matrix[tour[-1]][tour[0]]
	return tour_length

def coverage_path_planner(map_num, method, specs):
	"""
	Top function for coverage path planning.
	Accepts a map in the form of a sequence of points and bot specs.
	Return a coverage path.
	:param map_num: Id of a map
	:param method: Method to use for planning
	:param specs: Dict of specs of the bot
	:return path: Coverage path
	"""


	# Extract radius
	radius = specs["radius"]

	print("[%18s] Generating a polygon."%tk.current_time())
	P = dec.polygon_generator(map_num) ########### MAP NUMBER HERE!@!!!!!

	# Fire off the pipeline for particular method
	print("[%18s] Starting Coverage Path Planner."%tk.current_time())
	if method is Methods.min_alt_decomp:
		print("[%18s] Using %s method."%(tk.current_time(), method))

		print("[%18s] Invoking min alt decomposition."%tk.current_time())
		cvx_set, connectivity, shared_edges = dec.min_alt_decompose(P)
		print("[%18s] Finished min alt decomposition."%tk.current_time())

		print("[%18s] Startint to line sample in min direction."%tk.current_time())
		lines = lsmpl.min_alt_sampling(cvx_set, specs)
		print("[%18s] Finished samling."%tk.current_time())

		print("[%18s] Initializing GTSP cost matrix."%tk.current_time())
		dict_mapping = lsmpl.init_dict_mapping(lines)

		print("[%18s] Computing the cost matrix."%tk.current_time())
		cost_matrix, cluster_list = dc.init_cost_matrix(P, dict_mapping, lines, specs)
		print("[%18s] Launching GTSP instance."%tk.current_time())
		gtsp.generate_gtsp_instance("cpp_test", "/home/sbochkar/misc/GLKH-1.0/", True, cost_matrix, cluster_list)

		print("[%18s] Reading the results."%tk.current_time())
		tour = gtsp.read_tour("cpp_test")
		tour = gtsp.process_tour(tour, cluster_list)
		print("[%18s] Tour Cost: %5f"%(tk.current_time(), output_path_stats(lines, tour, cost_matrix)))


		print("[%18s] Plotting the results."%tk.current_time())		
		ax = splot.init_axis()

		print("[%18s] Plotting decomposition."%tk.current_time())
		splot.plot_decomposition(ax, cvx_set, shared_edges)

		print("[%18s] Plotting sampling."%tk.current_time())
		splot.plot_samples(ax, lines)

		print("[%18s] Plotting path."%tk.current_time())
		#splot.plot_tour(ax, tour, lines, dict_mapping)
		splot.plot_tour_dubins(ax, tour, lines, dict_mapping, radius)

		splot.display()


	elif method is Methods.greedy_decomp:
		print("[%18s] Using %s method."%(tk.current_time(), method))

		print("[%18s] Invoking greedy decomposition."%tk.current_time())
		cvx_set, connectivity, shared_edges = dec.greedy_decompose(P)
		print("[%18s] Finished greedy decomposition."%tk.current_time())

		print("[%18s] Startint to line sample in min direction."%tk.current_time())
		lines = lsmpl.min_alt_sampling(cvx_set, specs)
		print("[%18s] Finished samling."%tk.current_time())

		print("[%18s] Initializing GTSP cost matrix."%tk.current_time())
		dict_mapping = lsmpl.init_dict_mapping(lines)

		print("[%18s] Computing the cost matrix."%tk.current_time())
		cost_matrix, cluster_list = dc.init_cost_matrix(P, dict_mapping, lines, specs)
		print("[%18s] Launching GTSP instance."%tk.current_time())
		gtsp.generate_gtsp_instance("cpp_test", "/home/sbochkar/misc/GLKH-1.0/", True, cost_matrix, cluster_list)

		print("[%18s] Reading the results."%tk.current_time())
		tour = gtsp.read_tour("cpp_test")
		tour = gtsp.process_tour(tour, cluster_list)

		# Implementation missing for now
		# splot.plot_polygon_outline(ax, map_poly)
		print("[%18s] Tour Cost: %5f"%(tk.current_time(), output_path_stats(lines, tour, cost_matrix)))
		ax = splot.init_axis()

		print("[%18s] Plotting decomposition."%tk.current_time())
		splot.plot_decomposition(ax, cvx_set, shared_edges)

		print("[%18s] Plotting sampling."%tk.current_time())
		splot.plot_samples(ax, lines)

		print("[%18s] Plotting path."%tk.current_time())
		#splot.plot_tour(ax, tour, lines, dict_mapping)
		splot.plot_tour_dubins(ax, tour, lines, dict_mapping, radius)

		splot.display()

		
	elif method is Methods.grid_gtsp:
		# Grid the map
		# Generate cost
		# Launch GTSP
		print("[%18s] Discitization of space started."%(tk.current_time()))
		grid = psmpl.discritize_space_sqr(P, specs['radius'])

		print("[%18s] Generation of cost matrix."%(tk.current_time()))
		cost_matrix, next_mtx = dc.init_cost_matrix_grid(grid, specs['radius'])
		print("[%18s] Launching GTSP instance."%tk.current_time())
		gtsp.grid_to_gtsp_instance(cost_matrix, "gtsp_cpp", False)
		tour = gtsp.read_tour("gtsp_cpp")
		#tour = gtsp.process_tour(tour, cluster_list)
		print tour

		ax = splot.init_axis()
		splot.plot_polygon_outline(ax, P)
		splot.plot_grid(ax, grid)
		splot.plot_grid_tour(ax, grid, tour, next_mtx)
		splot.display()


	elif methos is Methods.local_line_sampling_2dir:
		print("[%18s] Using %s method."%(tk.current_time(), method))

		print("[%18s] Invoking greedy decomposition."%tk.current_time())
		cvx_set, connectivity, shared_edges = dec.greedy_decompose(P)
		print("[%18s] Finished greedy decomposition."%tk.current_time())

		print("[%18s] Startint to line sample in min direction."%tk.current_time())
		lines = lsmpl.min_alt_sampling(cvx_set, specs)
#		#lines = lsmpl.ilp_finite_dir_line_sampling(cvx_set, connectivity, shared_edges, [0, math.pi/2], specs)
#		print lines
#		#print lines[0][0][0]
#		#temp = lines[0][0][0]
#		#lines[0][0][0] = lines[0][0][1]
#		#lines[0][0][1] = temp
#		#print lines[0][0][0]
		print("[%18s] Finished samling."%tk.current_time())
#
		print("[%18s] Initializing GTSP cost matrix."%tk.current_time())
		dict_mapping = lsmpl.init_dict_mapping(lines)
#
		print("[%18s] Computing the cost matrix."%tk.current_time())
		#cost_matrix, cluster_list = sc.init_cost_matrix(dict_mapping, lines)
		cost_matrix, cluster_list = dc.init_cost_matrix(P, dict_mapping, lines, specs)
		print("[%18s] Launching GTSP instance."%tk.current_time())
		gtsp.generate_gtsp_instance("cpp_test", "/home/sbochkar/misc/GLKH-1.0/", True, cost_matrix, cluster_list)
	

if __name__ == "__main__":

	mappp = 0
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

	specs = {"radius": 0.2}
	map_num = 5
	coverage_path_planner(map_num, Methods.min_alt_decomp, specs)
	#coverage_path_planner(map_num, Methods.greedy_decomp, specs)
	#coverage_path_planner(map_num, Methods.grid_gtsp, specs)