# Modules import
from math import cos
from math import sin
from math import pi
from operator import itemgetter


def rotate(vertices, theta):
	""" Rotate a set of vertices by theta

	Rotate a set of vertices consisting of (x,y) tuples by applygin rigid
	transformation

	Args:
		vertices: list of (x, y) coordinates
		theta: the angle of rotation

	Returns:
		None
	"""

	cos_th = cos(theta)
	sin_th = sin(theta)

	n = len(vertices)
	if not n:
		print "rotate: points list EMPTY!"
		return None

	new_points = []
	for i in range(n):
		x_new = vertices[i][0]*cos_th-vertices[i][1]*sin_th
		y_new = vertices[i][0]*sin_th+vertices[i][1]*cos_th

		new_points.append( (x_new, y_new) )

	return new_points


def get_altitude(P, theta):
	""" Compute the altitude of polygon P with respect to direction theta.

	Performs rotation of the polygon as to align with x-axis. Perform a
	simplified trapezoidal sweep to compute the altitude.

	Args:
		P: polygon specified in the form of a tuple (ext, [int]). ext is a list
			of (x, y) tuples specifying the exterior of a polygon ccw. [int] is
			a list of lists of (x, y) tupeles specifying holes of a polygon cw.
		theta: angle of measurement with respect to x-axis

	Returns:
		altitude: A scalar value of the altitude
	"""

	ext_orig = P[0]
	if len(P) > 1:
		holes_orig = P[1] 


	ext = rotate(ext_orig, -theta)

	holes = []
	for hole in holes_orig:
		holes.append(rotate(hole, -theta))

	ext_sorted = sorted(ext, key=itemgetter(1))

	holes_sorted = []
	for hole in holes_sorted:
		holes_sorted.append(sorted(hole, key=itemgetter(1)))

if __name__ == "__main__":

	ext = [(0, 0),
			(10, 0),
			(10, 10),
			(0, 10)]

	holes = [
				[(1, 1),
					(2, 1),
					(2, 2),
					(1, 2)],
				[(8,8),
			 		(9, 8),
			 		(9, 9),
			 		(8, 9)]
			]

	get_altitude([ext, holes], 0)
