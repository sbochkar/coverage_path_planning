from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import LinearRing
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point

from decimal import Decimal
from decimal import getcontext


def decomposing_line_cut_by_splicing(P, v, w):
	"""Decomposing cut splitting a polygon into two.

	Decomposing cut which operates on a single simple chain. It is important
	that P be a simple chain for decomposing cut to generate a shape. If a cut
	is connecting two chains then such cut us an intermediate cut.

	The cut is an edge from v to w that splits polygons P into two. This
	function performs the cut as a line from v to w.

	Assumptions:
		* v and w both are on the chain on P
		* The resultant polygons will not contain any holes
		* v and w are not adjacent, otherwise returns a line and a polygon

	Args:
		P: Polygon as a tuple (ext, inters)
		v: vertex in P where the cut originiates at
		w: vertex in P where the cut terminates at

	Returns:
		p_l: Polygon on the left of a cut
		p_r: Polygon on the right of a cut
	"""


	v_Point = Point(v)
	w_Point = Point(w)

	chain = LineString(P[0]+[P[0][0]])

	distance_to_v = chain.project(v_Point)
	distance_to_w = chain.project(w_Point)

	if not chain.intersects(v_Point):
		print("decomposing_cut_as_line: V not on chain")
	if not chain.intersects(w_Point):
		print("decomposing_cut_as_line: W not on chain")
	if distance_to_w == distance_to_v:
		print("decomposing_cut_as_line: W and V are the same")


	if distance_to_w >= chain.length or distance_to_w == 0:

		left_chain, right_chain = cut_linestring(chain, distance_to_v)

		p_l = left_chain.coords[:]
		p_r = right_chain.coords[:]		

		return p_l, p_r

	if distance_to_v >= chain.length or distance_to_v == 0:

		left_chain, right_chain = cut_linestring(chain, distance_to_w)

		p_l = right_chain.coords[:]
		p_r = left_chain.coords[:]		

		return p_l, p_r


	if distance_to_w > distance_to_v:

		left_v_cut, right_v_cut = cut_linestring(chain, distance_to_v)

		distance_to_w = right_v_cut.project(w_Point)
		left_w_chain, right_w_chain = cut_linestring(right_v_cut, distance_to_w)

		p_l = left_v_cut.coords[:]+right_w_chain.coords[:-1]
		p_r = left_w_chain.coords[:]

		return p_l, p_r

	else:

		left_w_cut, right_w_cut = cut_linestring(chain, distance_to_w)

		distance_to_v = right_w_cut.project(v_Point)
		left_v_chain, right_v_chain = cut_linestring(right_w_cut, distance_to_v)

		p_l = left_w_cut.coords[:]+right_v_chain.coords[:-1]
		p_r = left_v_chain.coords[:]

		return p_l, p_r


def cut_linestring(line, distance):
	"""Shapely implementation of a cut

	Splicing a LineString into two separating a distance from start
	Credits go to author of the shapely manual

	Args:
		line: LineString representation of a line
		distance: Scalar representing the distance from start of the line

	Returns:
		left: Part of line on the left of cut point
		right: Part of line on the right of cut point
	"""

	pd = 0

	distance = distance % line.length

	if distance == 0.0:
		return [line, []]


	coords = list(line.coords)
	for i in range(1, len(coords)):
		
		pd = LineString(coords[:i+1]).length

		if pd == distance:
			return [
				LineString(coords[:i+1]),
				LineString(coords[i:])]

		if pd > distance:
			cp = line.interpolate(distance)
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]


def decomposing_poly_cut_by_set_op(P, v, w, epsilon=10e-2):
	"""Decomposing cut splitting a polygon into two where cut is a thin box.

	Decomposing cut which operates on a single simple chain. It is important
	that P be a simple chain for decomposing cut to generate a shape. If a cut
	is connecting two chains then such cut us an intermediate cut.

	The cut is an edge from v to w that splits polygons P into two. This
	function performs the cut as a rectangle of width 2*epsilon to enforce small
	separation distance between polygons. This is done for practical reasons to
	avoid polygons with selft intersecting chains.

	Assumptions:
		* cut is in the interior of P

	Args:
		P: Polygon as a tuple (ext, inters)
		v: vertex in P where the cut originiates at
		w: vertex in P where the cut terminates at

	Returns:
		p_l: Polygon on the left of a cut
		p_r: Polygon on the right of a cut
	"""


	getcontext().prec = 28

	v_Point = Point(v)
	w_Point = Point(w)

	chain = LineString(P[0]+[P[0][0]])

	if not chain.intersects(v_Point):
		print("decomposing_poly_cut_as_line: V not on chain")
	if not chain.intersects(w_Point):
		print("decomposing_poly_cut_as_line: W not on chain")


	distance_to_v = chain.project(v_Point)
	distance_to_w = chain.project(w_Point)

	if distance_to_w == distance_to_v:
		print("decomposing_cut_as_line: W and V are the same")


	# Generate pairs of v and w modified by some epsilon amount 
	v_l_displacements = [distance_to_v+(i*epsilon) for i in [-1, -2, 0]]
	v_r_displacements = [(distance_to_v+(i*epsilon))%chain.length for i in [1, 0, 2]]
	w_l_displacements = [distance_to_w+(i*epsilon) for i in [-1, -2, 0]]
	w_r_displacements = [(distance_to_w+(i*epsilon))%chain.length for i in [1, 0, 2]]

	def splice_polygon(dist_v, dist_w):
		"""Portion of decomposing_line_cut_by_splicing wihtout points

		Function for evaluating validity of candidates
		"""

		if dist_w >= chain.length or dist_w == 0:

			left_chain, right_chain = cut_linestring(chain, dist_v)

			p_l = left_chain.coords[:]
			p_r = right_chain.coords[:]		

			return p_l, p_r

		if dist_v >= chain.length or dist_v == 0:

			left_chain, right_chain = cut_linestring(chain, dist_w)

			p_l = right_chain.coords[:]
			p_r = left_chain.coords[:]		

			return p_l, p_r


		if dist_w%chain.length > dist_v%chain.length:

			left_v_chain, right_v_chain = cut_linestring(chain, dist_v)
			left_w_chain, right_w_chain = cut_linestring(chain, dist_w)

			common = LineString(left_w_chain).difference(LineString(left_v_chain))

			p_l = left_v_chain.coords[:]+right_w_chain.coords[:-1]
			p_r = common.coords[:]

			return p_l, p_r

		else:

			left_v_chain, right_v_chain = cut_linestring(chain, dist_v)
			left_w_chain, right_w_chain = cut_linestring(chain, dist_w)

			common = LineString(left_v_chain).difference(LineString(left_w_chain))

			p_l = common.coords[:]
			p_r = left_w_chain.coords[:]+right_v_chain.coords[:-1]

			return p_l, p_r

	# Check every ring for self-intersection, if cut is invalid => self-intersec
	found = False
	for i in range(len(v_l_displacements)):
		for j in range(len(w_l_displacements)):

			# Check if resultant polygons are valid
			p_l, p_r = splice_polygon(v_l_displacements[i], w_r_displacements[j])
			p_l_lr = LinearRing(p_l+[p_l[0]])
			p_r_lr = LinearRing(p_r+[p_r[0]])

			if not p_l_lr.is_valid or not p_r_lr.is_valid:
				continue

			p_l, p_r = splice_polygon(v_r_displacements[i], w_l_displacements[j])
			p_l_lr = LinearRing(p_l+[p_l[0]])
			p_r_lr = LinearRing(p_r+[p_r[0]])

			if not p_l_lr.is_valid or not p_r_lr.is_valid:
				continue

			# Else, we have a valid candidate cut
			found = True
			break

		if found:
			break

	if not found:
		print("splice_polygon: No correct cut combination found!")
		return

	cut_pt_1 = chain.interpolate(v_l_displacements[i]).coords[:]
	cut_pt_2 = chain.interpolate(v_r_displacements[i]).coords[:]
	cut_pt_3 = chain.interpolate(w_l_displacements[j]).coords[:]
	cut_pt_4 = chain.interpolate(w_r_displacements[j]).coords[:]

	cut_poly = Polygon(cut_pt_1+cut_pt_2+cut_pt_3+cut_pt_4)
	print cut_poly

#	# Filter result by the geometric type
#	if result.geom_type == "MultiPolygon":
#
#		resultant_polys = list(result)
#		print resultant_polys[1]
#		if len(resultant_polys) > 2:
#			print("poly_cut_by_set_op: Forbidden cut generated more then 2 polygons")
#
#		# Convert to vertex representation of poylgons
#		holes = []
#		p_l = [list(resultant_polys[0].exterior.coords)]
#		for hole in list(resultant_polys[0].interiors):
#			holes.append(hole.coords[:])
#		p_l.append(holes)
#
#		holes = []
#		p_r = [list(resultant_polys[1].exterior.coords)]
#		for hole in list(resultant_polys[1].interiors):
#			holes.append(hole.coords[:])
#		p_r.append(holes)
#
#		return p_l, p_r
#
#	elif result.geom_type == "Polygon":
#		
#		holes = []
#		p_l = [list(result.exterior.coords)]
#		for hole in list(result.interiors):
#			holes.append(hole.coords[:])
#		p_l.append(holes)
#
#		return p_l, None




ext = [(0.0, 0.0),
		(4.0,  0.0),
		(5.0,  1.0),
		(6.0,  0.0),
		(10.0, 0.0),
		(10.0, 5.0),
		(6.0,  5.0),
		(5.0,  4.0),
		(4.0,  5.0),
		(0.0,  5.0)]

holes = [
			[(6,1),
			(6,4),
			(9,4),
			(9,1)]
		]
P = [ext, holes]


print decomposing_poly_cut_by_set_op(P, (0,10e-2), (5,1))
