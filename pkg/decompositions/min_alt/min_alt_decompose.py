

def min_alt_decompose(P):
	"""
	Min altitude decomposition.

	1: Connect all simple chains of a polygon
	2: Perform a series of decomposing cuts
	3: Run an iterative minimization step to reoptimize cuts

	:param P: Polygin in the standard form
	:return decomposition: A set of polygons
	"""

	min_alt, theta = alt.get_min_altitude(P)
	D, active_verts = alt.combine_chains(P, theta)
	#R = alt.find_reflex_vertices(D)
	#print("Reflex set: %s"%(R,))
	cut = alt.find_optimal_cut(poly, v)

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
