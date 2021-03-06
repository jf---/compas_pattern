import compas

from compas_pattern.algorithms.decomposition.mapping import surface_discrete_mapping
from compas_pattern.algorithms.decomposition.triangulation import boundary_triangulation

from compas_pattern.algorithms.decomposition.skeletonisation import Skeleton
from compas_pattern.algorithms.decomposition.decomposition import Decomposition

from compas_pattern.cad.rhino.objects.surface import RhinoSurface

from compas.utilities import geometric_key

__all__ = [
	'surface_decomposition',
	'decomposition_delaunay',
	'decomposition_skeleton',
	'decomposition_curves',
	'decomposition_mesh',
	'decomposition_polysurface'
]


def surface_decomposition(srf_guid, precision, crv_guids=[], pt_guids=[]):
	"""Generate the topological skeleton/medial axis of a surface based on a Delaunay triangulation, after mapping and before remapping.

	Parameters
	----------
	srf_guid : guid
		A Rhino surface guid.
	precision : float
		A discretisation precision.
	crv_guids : list
		A list of Rhino curve guids.
	pt_guids : list
		A list of Rhino points guids.

	Returns
	-------
	decomposition : Decomposition
		The decomposition of the surface and its features.

	References
	----------
	.. [1] Harry Blum. 1967. *A transformation for extracting new descriptors of shape*.
		   Models for Perception of Speech and Visual Forms, pages 362--380.
		   Available at http://pageperso.lif.univ-mrs.fr/~edouard.thiel/rech/1967-blum.pdf.
	.. [2] Punam K. Saha, Gunilla Borgefors, and Gabriella Sanniti di Baja. 2016. *A survey on skeletonization algorithms and their applications*.
		   Pattern Recognition Letters, volume 76, pages 3--12.
		   Available at https://www.sciencedirect.com/science/article/abs/pii/S0167865515001233.
	.. [3] Oval et al. 2019. *Feature-based topology finding of patterns for shell structures*.
		   Accepted in Automation in Construction.

	"""

	# mapping NURBS surface to planar polyline borders
	outer_boundary, inner_boundaries, polyline_features, point_features = surface_discrete_mapping(srf_guid, precision, crv_guids = crv_guids, pt_guids = pt_guids)

	# Delaunay triangulation of the palnar polyline borders
	decomposition = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features, cls=Decomposition)

	return decomposition, outer_boundary, inner_boundaries, polyline_features, point_features

def decomposition_delaunay(srf_guid, decomposition):
	# output remapped Delaunay mesh
	return RhinoSurface(srf_guid).mesh_uv_to_xyz(decomposition)

def decomposition_skeleton(srf_guid, decomposition):
	# output remapped topological skeleton/medial axis
	return [RhinoSurface(srf_guid).polyline_uv_to_xyz([xyz[:2] for xyz in polyline]) for polyline in decomposition.branches()]

def decomposition_curves(srf_guid, decomposition):
	return [RhinoSurface(srf_guid).polyline_uv_to_xyz([xyz[:2] for xyz in polyline]) for polyline in decomposition.decomposition_polylines()]

def decomposition_mesh(srf_guid, decomposition, point_features):
	# output decomposition coarse quad mesh
		mesh = decomposition.decomposition_mesh(point_features)
		RhinoSurface.from_guid(srf_guid).mesh_uv_to_xyz(mesh)
		return mesh

def decomposition_polysurface(srf_guid, decomposition, point_features):
	mesh = decomposition.decomposition_mesh()
	nurbs_curves = {(geometric_key(polyline[i]), geometric_key(polyline[-i -1])): rs.AddInterpCrvOnSrfUV(srf_guid, [pt[:2] for pt in polyline]) for polyline in decomposition.decomposition_polylines() for i in [0, -1]}
	polysurface = rs.JoinSurfaces([rs.AddEdgeSrf([nurbs_curves[(geometric_key(mesh.vertex_coordinates(u)), geometric_key(mesh.vertex_coordinates(v)))] for u, v in mesh.face_halfedges(fkey)]) for fkey in mesh.faces()], delete_input=True)
	rs.DeleteObjects(list(nurbs_curves.values()))
	return polysurface

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh.mesh import Mesh
	#from compas_pattern.algorithms.decomposition.decomposition import Decomposition

	outer_boundary = [[1.0, 0.125, 0.0], [1.0, 0.25, 0.0], [1.0, 0.375, 0.0], [1.0, 0.5, 0.0], [1.0, 0.625, 0.0], [1.0, 0.75, 0.0], [1.0, 0.875, 0.0], [1.0, 1.0, 0.0], [0.875, 1.0, 0.0], [0.75, 1.0, 0.0], [0.625, 1.0, 0.0], [0.5, 1.0, 0.0], [0.375, 1.0, 0.0], [0.25, 1.0, 0.0], [0.125, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.875, 0.0], [0.0, 0.75, 0.0], [0.0, 0.625, 0.0], [0.0, 0.5, 0.0], [0.0, 0.375, 0.0], [0.0, 0.25, 0.0], [0.0, 0.125, 0.0], [0.0, 0.0, 0.0], [0.125, 0.0, 0.0], [0.25, 0.0, 0.0], [0.375, 0.0, 0.0], [0.5, 0.0, 0.0], [0.625, 0.0, 0.0], [0.75, 0.0, 0.0], [0.875, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.125, 0.0]]
	point_features = [[0.29999999999999999, 0.59999999999999998, 0.0]]

	decomposition = boundary_triangulation(outer_boundary, inner_boundaries=[], polyline_features=[], point_features=point_features, cls=Decomposition)
