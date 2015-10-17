#!/usr/bin/env python3

# Global moduls
import os, sys, inspect
from enum import Enum

# Local modules
cmd_subfolder = os.path.realpath(os.path.abspath(
				os.path.join(os.path.split(
				inspect.getfile( inspect.currentframe() ))[0],"time_keeping")))

if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)

cmd_subfolder = os.path.realpath(os.path.abspath(
				os.path.join(os.path.split(
				inspect.getfile( inspect.currentframe() ))[0],"decomposer")))

if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)


import time_keeping as tk


# Define Enum for methods
class Methods(Enum):
	map_grid_sampling = 0
	local_line_sampling = 1


def coverage_path_planner(map_poly, method, specs):
	"""
	Top function for coverage path planning.
	Accepts a map in the form of a sequence of points and bot specs.
	Return a coverage path.
	:param map_poly: A list of (x, y) tuples representing a map
	:param method: Method to use for planning
	:param specs: Dict of specs of the bot
	:return path: Coverage path
	"""


	# Check the map validity
	if len(map_poly) < 3:
		print("[%18s] Error! Map specification is wrong."%tk.current_time())
		return None

	# Extract radius
	radius = specs["r"]

	# Fire off the pipeline for particular method
	print("[%18s] Starting Coverage Path Planner."%tk.current_time())
	if method is Methods.local_line_sampling:
		print("[%18s] Using %s method."%(tk.current_time(), method))






if __name__ == "__main__":

	map_poly = [(0, 0), (5, 0), (2, 4)]

	specs = {"r": 0.5}

	coverage_path_planner(map_poly, Methods.local_line_sampling, specs);