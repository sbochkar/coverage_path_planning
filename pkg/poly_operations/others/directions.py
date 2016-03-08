from math import atan2
from math import pi


def get_directions_set(P):
	"""
	Generate a list of directions orthogonal to edges of P

	TODO: Get rid of repeating directions

	Augs:
		P: standard form polygon
	Returns:
		dirs: set of directions [rad]
	"""


	ext = P[0]
	holes = P[1]
	dirs = []

	n = len(ext)
	for i in range(n):
		edge = [ext[i], ext[(i+1)%n]]
		#print edge
		ax, ay = edge[0]
		bx, by = edge[1]

		dirs.append(atan2(by-ay, bx-ax)+pi/2)


	for hole in holes:
		n = len(hole)
		for i in range(n):
			edge = [hole[i], hole[(i+1)%n]]
			ax, ay = edge[0]
			bx, by = edge[1]

			dirs.append(atan2(by-ay, bx-ax)+pi/2)

	return dirs