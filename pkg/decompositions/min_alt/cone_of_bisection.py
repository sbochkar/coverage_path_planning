from shapely.geometry import Polygon
from math import sqrt
from math import atan2
from math import pi
from math import cos
from math import sin
import numpy as np


def compute(P, v):
	"""
	Compute cone of bisection given a reflex vertex and P
	Inputs:
		P: standard form
		v: Reflex vertex with an id appended
	"""


	ext = P[0]
	holes = P[1]

	Pp = Polygon(P[0], P[1])

	minx, miny, maxx, maxy = Pp.bounds
	rad = sqrt((maxx-minx)**2+(maxy-miny)**2)	# "Dimater" of the polygon

	# Form an adjacency list for easy access to adjacent edges
	adj = adj_e.get_edge_adjacency_as_dict(P)
#	print adj
#	print P

	#Find adjacent edges of v
	v_l = adj[v][1][1]; v_r = adj[v][0][1]

	# Find the angle of v_l with the x-axis
	theta_l = atan2(v_l[1]-v[1][1], v_l[0]-v[1][0])
	theta_r = atan2(v_r[1]-v[1][1], v_r[0]-v[1][0])

	# Consider several cases which will determine the measurement for the cone of bisection
	if theta_l < 0 and theta_r < 0:
		angle = abs(theta_l-theta_r)
		orientation = pi+theta_l+angle/2
	elif theta_l <= 0 and theta_r >= 0:
		angle = theta_r-theta_l
		orientation = pi+theta_l+angle/2
	elif theta_l > 0 and theta_r > 0:
		angle = theta_r-theta_l
		orientation = pi+theta_l+angle/2
	elif theta_l > 0 and theta_r < 0:
		angle = 2*pi-(theta_l-theta_r)
		orientation = pi+theta_l+angle/2
	else:
		print("ERROR: CONE OF BISECTION<: IF DID NTO CAPTURE")

	p = []

	p.append(v[1])
	for i in np.arange(orientation-angle/2,orientation+angle/2,0.1):
		x = rad*cos(i)
		y = rad*sin(i)

		new_x = v[1][0]+x
		new_y = v[1][1]+y

		p.append((new_x, new_y))

	x = rad*cos(orientation+angle/2)
	y = rad*sin(orientation+angle/2)

	new_x = v[1][0]+x
	new_y = v[1][1]+y

	p.append((new_x, new_y))

	return p


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import rotation
		import reflex
else:
	from ...poly_operations.others import adjacency_edges as adj_e
