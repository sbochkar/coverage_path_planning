from math import acos
from math import pi
from math import sqrt


class LineSegment:
	def __init__(self, coords):
		self.coords = coords
		self.dirs_num = 2

		p1, p2 = coords

		vector_1 = p2[0]-p1[0], p2[1]-p1[1]
		vector_2 = p1[0]-p2[0], p1[1]-p2[1]

		v1_m = sqrt(vector_1[0]**2 + vector_1[1]**2)
		v2_m = sqrt(vector_2[0]**2 + vector_2[1]**2)

		v1_n = (vector_1[0]/v1_m, vector_1[1]/v2_m)
		v2_n = (vector_2[0]/v2_m, vector_2[1]/v2_m)

		dproduct_1 = v1_n[0]	# dproduct with x-axis
		dproduct_2 = v2_n[0]	# dproduct with x-axis

		# Need true angle rather than limited to [-pi, 0]
		if vector_1[1] < 0: dir_1 = -acos(dproduct_1)
		else: 				dir_1 = acos(dproduct_1)

		if vector_2[1] < 0: dir_2 = -acos(dproduct_2)
		else: 				dir_2 = acos(dproduct_2)

		self.dirs = [dir_2, dir_1]

	def get_exit_info(self, dir_num):

		return (self.coords[dir_num][0], self.coords[dir_num][1], self.dirs[dir_num])

	def get_entrance_info(self, dir_num):

		return (self.coords[(dir_num+1)%2][0], self.coords[(dir_num+1)%2][1], self.dirs[dir_num])

	def get_length(self):
		x0, y0 = self.coords[0]
		x1, y1 = self.coords[1]

		return sqrt((x1-x0)**2 + (y1-y0)**2)

class PointSegment:
	def __init__(self, coord):
			self.coord = coord
			self.dirs_num = 8
			self.dirs = [i*pi/2 for i in range(9)]

	def get_exit_info(self, dir_num):
		return (self.coord[0], self.coord[1], self.dirs[dir_num])

	def get_entrance_info(self, dir_num):
		return (self.coord[0], self.coord[1], self.dirs[dir_num])

	def get_length(self):
		return 0.0
