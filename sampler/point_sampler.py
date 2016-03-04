import math
import numpy as np
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import Point


def discritize_space_sqr(P, r):
	"""
	This function will generate a lattice inside a polygon.
	The lattice will be a function of the radius of the sweeping tool.
	The points are generated as if the polygon was tiled with hexagons if radius r.
	The grid points are the center-points of the hexagons.
	:param P: A shapely Polygob object representing the P
	:param r: Radius of the circular sweeping tool
	:return: List of grid points
	"""

	## Shrink the P
	P = Polygon(*P)
	new_P = P.exterior.parallel_offset(r, 'left')
	minx, miny, maxx, maxy = new_P.bounds

	x_spacing = r*math.sqrt(2)
	y_spacing = r*math.sqrt(2)

	x_range = list(np.arange(minx, maxx, x_spacing))
	y_range = list(np.arange(miny, maxy, y_spacing))

	## Test if points are inside the polygon, and generate a list of points
	pts = []
	for i in range(len(y_range)):
		for j in range(len(x_range)):
			pt = Point((x_range[j], y_range[i]))

			if not P.intersection(pt).is_empty:
				pts.append((pt.x, pt.y))
	## ----------------------------------------------------------------
	return pts