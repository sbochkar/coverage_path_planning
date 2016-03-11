

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
	P_fused, active_verts = chain_combination.combine_chains(P, theta)

	#print("After chain combination: %s"%D)
	R = reflex.find_reflex_vertices(P_fused)
	#print("Reflex set: %s"%(R,))

	# For bring up testing, make just one cut
	# Since D is one chain, we can just pass D. However for later passes, need to find a polygon in D before passing to this function
	D = P_fused
	while R:
		v = R.pop()
		cut = cuts.find_optimal_cut(P_fused, v)
		print("Ref: %s"%(v[1],))
		print("Cut: %s"%(cut,))
		#if cut or cut is not None: # Not empty
			#p_l, p_r = cuts.perform_cut(D, [v[1], cut[0]])
			#print("Left poly: %s"%(p_l,))
			#print("Right poly: %s"%(p_r,))
			#D.append([p_l, []])
			#D.append([p_r, []])

	#print D
	return D
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
