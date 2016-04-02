from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point


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
		print "decomposing_cut_as_line: V not on chain"
	if not chain.intersects(w_Point):
		print "decomposing_cut_as_line: W not on chain"
	if distance_to_w == distance_to_v:
		print "decomposing_cut_as_line: W and V are the same"


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


def decomposing_poly_cut_by_set_op(P, v, w, epsilon=10e-6):
	"""Decomposing cut splitting a polygon into two.

	Decomposing cut which operates on a single simple chain. It is important
	that P be a simple chain for decomposing cut to generate a shape. If a cut
	is connecting two chains then such cut us an intermediate cut.

	The cut is an edge from v to w that splits polygons P into two. This
	function performs the cut as a rectangle of width 2*epsilon to enforce small
	separation distance between polygons. This is done for practical reasons to
	avoid polygons with selft intersecting chains.

	Assumptions:
		* v and w both are on the chain on P
		* v and w are not adjacent, otherwise returns a line and a polygon

	Args:
		P: Polygon as a tuple (ext, inters)
		v: vertex in P where the cut originiates at
		w: vertex in P where the cut terminates at

	Returns:
		p_l: Polygon on the left of a cut
		p_r: Polygon on the right of a cut
	"""


	poly = Polygon(*P)
	line_seed = LineString([v, w])
	cut_poly = line_seed.buffer(epsilon, cap_style=2)

	result = poly.symmetric_difference(cut_poly)

	if result.geom_type == "MultiPolygon":

		for poly in list(result):
			print poly.exterior

	elif result.geom_type == "Polygon":
		pass




P = [(0,0), (10,0),(10,10),(0,10)], [[(4,4),(4,6),(6,6),(6,4)]]
decomposing_poly_cut_by_set_op(P, (4,4), (0,0))