from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import LinearRing


def combine_chains(P, theta):
	"""
	Combine the simple chains to form one non simple chain.
	This is to allow decomposing cuts. The combination cuts are oriented at theta.
	"""

	active_verts = []

	P = rotation.rotate_polygon(P, -theta)
	minx, miny, maxx, maxy = Polygon(*P).bounds

	chains = []
	for hole in P[1]:
		chains.append(hole)
	chains.append(P[0])

	# Loop over the whole chain dict except the last case
	for i in range(len(chains)-1):
		chain = chains[i]
		R = reflex.find_reflex_vertices([chain, []])

		for v in R:
			#print("Reflex v: %s"%(v,))
			hyperplane = LineString([(v[1][0],maxy), (v[1][0],miny)])
			print("Hyperplane: %s"%hyperplane)

			# Initialize up and down arrays
			up = []; down = []

			for j in range(len(chains)):
				print chains[j]
				intersection = hyperplane.intersection(LinearRing(chains[j]))

				# Empty intersection means other holes weren't aligned with the
				# hyperplane therefore no intersection is expected
				#print("Isection Type: %s"%intersection.geom_type)
				if intersection.is_empty: continue
				print("Intersection: %s"%intersection)
				points = get_points_from_intersection(intersection)
				print("Points from intersection: %s"%points)

				# Insert intersections into respective arrays
				for x, y in points:
					if y > v[1][1]:
						up.append(((x,y), j))
						continue
					elif y < v[1][1]:
						down.append(((x,y), j))
						continue
					elif y == v[1][1]:
						up.append(((x,y), j))
						down.append(((x,y), j))
						continue


			# Sort the up and down arrays
			up = sorted(up, key=lambda elem: elem[0][1])
			down = sorted(down, key=lambda elem: elem[0][1])
			#print("Up: %s"%up)
			#print("Down: %s"%down)
			# If closest points is hole itself, go to the next reflex vertex
			if (up[1][1] == i) and (down[-2][1] == i): continue
			if up[1][1] == i: cut_parameters = down[-2]; break
			if down[-2][1] == i: cut_parameters = up[1]; break
			cut_parameters = up[1]; break # Maybe need to choose smartly

		#print("Cutting from: %s to %s"%(v, cut_parameters))
		orig_chain = LineString(chain+[chain[0]])
		dest_chain = LineString(chains[cut_parameters[1]]+[chains[cut_parameters[1]][0]])
		#print orig_chain, dest_chain

		distance_to_v = orig_chain.project(Point(v[1]))
		distance_to_w = dest_chain.project(Point(cut_parameters[0]))
		#print("Dist_v: %2f, Dist_w: %2f"%(distance_to_v, distance_to_w))
		#print("Orig_l: %2f, Dist_l: %2f"%(orig_chain.length, dest_chain.length))

		if distance_to_v == 0:
			orig_chain_1 = []; orig_chain_2 = orig_chain.coords[:]
		else:
			orig_chain_1, orig_chain_2 = cut(orig_chain, distance_to_v)
		if distance_to_w == 0:
			dest_chain_1 = []; dest_chain_2 = dest_chain.coords[:]
		else:
			dest_chain_1, dest_chain_2 = cut(dest_chain, distance_to_w)
			#print cut(dest_chain, distance_to_w)

		#if LinearRing(dest_chain).is_ccw:
		final_chain = dest_chain_1.coords[:]+\
						orig_chain_2.coords[:-1]+\
						orig_chain_1.coords[:]+\
						dest_chain_2.coords[:-1]

		# Now modify the chains array accoridngly to propagate the fusion method
		if cut_parameters[1] == (len(chains)-1):
			chains[len(chains)-1] = final_chain
		else:
			chains[cut_parameters[1]] = final_chain

		active_verts.append(v)
		print("Active verts: %s"%active_verts)
		print("Final chain: %s"%final_chain)
	return rotation.rotate_polygon([chains[len(chains)-1],[]], theta), active_verts


def get_points_from_intersection(intersection):

	if intersection.geom_type == "Point":
		return [(intersection.x, intersection.y)]
	elif intersection.geom_type == "MultiPoint":
		return [(point.x, point.y) for point in intersection]
	elif intersection.geom_type == "LineString":
		return [point for point in intersection.coords[:]]
	elif intersection.geom_type == "MultiLineString":
		points = []
		for line in intersection:
			points.extend([point for point in line.coords[:]])
		return points
	elif intersection.geom_type == "GeometryCollection":
		#print intersection
		points = []
		for item in intersection:
			points.extend(get_points_from_intersection(item))
		return points


def cut(line, distance):
	"""
	Splicing a line
	Credits go to author of the shapely manual
	"""
	# Cuts a line in two at a distance from its starting point
	if distance <= 0.0 or distance >= line.length:
		return [LineString(line)]
	coords = list(line.coords)
	for i, p in enumerate(coords):
		pd = line.project(Point(p))
		if pd == distance:
			return [
				LineString(coords[:i+1]),
				LineString(coords[i:])]
		if pd > distance:
			cp = line.interpolate(distance)
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]
		if i == len(coords)-1:
			cp = line.interpolate(distance)
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]



if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import rotation
		import reflex
		
		print combine_chains([[(0,0)],[]], 0)
else:
	from ...aux.geometry import rotation
	import reflex
