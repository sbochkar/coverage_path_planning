import math
import numpy as np
from shapely.geometry import LineString
from shapely.geometry import LinearRing
from shapely.geometry import Polygon
from shapely.geometry import Point


def discritize_polygon(P, r):
	"""
	This function will generate a lattice inside a polygon.
	The lattice will be a function of the radius of the sweeping tool.
	The points are generated as if the polygon was tiled with hexagons if radius r.
	The grid points are the center-points of the hexagons.
	:param P: A shapely Polygob object representing the P
	:param r: Radius of the circular sweeping tool
	:return: List of grid points
	"""

	separation_distance = r*math.sqrt(2)

	## Shrink the P
	ext = LinearRing(P[0]).parallel_offset(r, 'left')

	interiors = []
	for hole in P[1]:
		interior = LinearRing(hole).parallel_offset(r, 'left')
		interiors.append(interior.coords[:])

	new_P = Polygon(ext.coords[:], interiors)
	minx, miny, maxx, maxy = new_P.bounds


	x_range = list(np.arange(minx, maxx, separation_distance))
	y_range = list(np.arange(miny, maxy, separation_distance))

	## Test if points are inside the polygon, and generate a list of points
	segments = []
	for i in range(len(y_range)):
		for j in range(len(x_range)):
			pt = Point((x_range[j], y_range[i]))

			if new_P.intersects(pt):
				segments.append(classes.PointSegment((pt.x, pt.y)))
	## ----------------------------------------------------------------
	return segments


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import edges
		from aux.altitudes import altitude as alt
		from aux.geometry import rotation

		sys.path.insert(0, os.path.abspath(".."))
		import classes
else:
	from ...aux.geometry import rotation
	from ...aux.altitudes import altitude as alt
	from ...poly_operations.others import directions
	from .. import classes