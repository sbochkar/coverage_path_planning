import operator


def decompose(P):
	"""
	Min altitude decomposition.

	1: Connect all simple chains of a polygon
	2: Perform a series of decomposing cuts
	3: Run an iterative minimization step to reoptimize cuts

	:param P: Polygin in the standard form
	:return decomposition: A set of polygons
	"""

	min_alt, theta = alt.get_min_altitude(P)
	#print("Min Alt: %2f, Theta: %2f"%(min_alt, 180*theta/3.14))
	P_fused, modified_edges = chain_combination.combine_chains(P, theta)


	#D = recursive_cuts(P_fused)
	recursive_cuts(P_fused)
	#print("List of polygons after recursion: %s"%(list_of_polygons,))

	# Need a smarter way of doing this
	#if len(D) == 2:
	#	if not D[1]:
	#		D = [D]


	return list_of_polygons

#	D = [P_fused]
#	print("Modified edges: %s"%(modified_edges,))

#	R = reflex.find_reflex_vertices(P_fused)
#	print("Reflex set: %s"%(R,))
#
#	# Createa a dict associating reflex vertices with polygons
#	ref_dict = {}
#	for vert in R:
#		ref_dict[vert] = 0
		
	# For bring up testing, make just one cut
	# Since D is one chain, we can just pass D. However for later passes, need to find a polygon in D before passing to this function

#	while ref_dict:
#		v, p_id = ref_dict.popitem()
#		#print("Poped vert: %s, id:%d"%(v, p_id))
#
#		cut = cuts.find_optimal_cut(D[p_id], v)
#		#print("Ref: %s"%(v[1],))
#		#print("Cut: %s"%(cut,))
#
#		if cut and cut is not None: # Not empty
#			p_l, p_r = cuts.perform_cut(D[p_id], [v[1], cut[0]])
#
#			# Uodate the dictionary accordingly
#			R_l = reflex.find_reflex_vertices([p_l, []])
#			for vertex in R_l:
#				ref_dict[vertex] = p_id
#
#			R_r = reflex.find_reflex_vertices([p_r, []])
#			p_id_max = max(ref_dict.values())
#			for vertex in R_r:
#				ref_dict[vertex] = p_id_max+1
#
#			#print("Left poly: %s"%(p_l,))
#			#print("Right poly: %s"%(p_r,))
#			D.pop(p_id)
#			D.insert(p_id, [p_l, []])
#			D.append([p_r, []])
#
#	#print D
#	return D
#	print("Active verts: %s"%(active_verts,))
#	cut = alt.find_optimal_cut(poly, v)

#	D = [[D, []]]
#	while R:
#		v = R.pop()
#		for poly in D:
#			if v in poly[0]:
#				break
#
#		R_temp = alt.find_reflex_vertices(poly)
#		if v not in R_temp:
#			continue
#
#		#print poly
#		#print v
#		cut = alt.find_optimal_cut(poly, v)
#		#print cut
#		# If best cut did not improve
#		if cut is None:
#			continue
#		#print poly, v, cut[0]
#		p_l, p_r = alt.perform_cut(poly,[v,cut[0]])
#		#print "New polygons"
#		#print p_l, p_r
#		D.remove(poly)
#		D.append([p_l, []])
#		D.append([p_r, []])
#		#print D
#		#print "Finished loop"

list_of_polygons = []
def recursive_cuts(P):
	"""
	Recursive cut of Polygon
	"""

	R = reflex.find_reflex_vertices(P)
	while R:
		v = R.pop()

		cut = cuts.find_optimal_cut(P, v)
		#print("Ref: %s"%(v[1],))
		#print("Cut: %s"%(cut,))

		if cut and cut is not None: # Not empty
			p_l, p_r = cuts.perform_cut(P, [v[1], cut[0]])

			#return [recursive_cuts([p_l,[]]), recursive_cuts([p_r,[]])]
			recursive_cuts([p_l,[]])
			recursive_cuts([p_r,[]])
			return
	#return P
	list_of_polygons.append(P)


if __name__ == '__main__':
	if __package__ is None:
		import os, sys
		sys.path.insert(0, os.path.abspath("../.."))
		from aux.geometry import rotation
		import reflex
else:
	from ...aux.altitudes import altitude as alt
	from ...decompositions.min_alt import cuts
	from ...poly_operations.others import chain_combination
	from ...poly_operations.others import reflex
