from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'unweld_mesh_along_edge_path',
]

def unweld_mesh_along_edge_path(mesh, edge_path):
    """Unwelds a mesh along an edge path.
    The vertices along the edge path are duplicated and the corresponding faces updated.
    An exception is made for the vertices at the extemities if they are not on the boundary.

    Parameters
    ----------
    mesh : Mesh
    edge_path: list
        List of successive edges.

    Returns
    -------
    mesh : Mesh
        The unwelded mesh.

    Raises
    ------
    -

    """
    
    duplicates = []

    # convert edge path in vertex path
    vertex_path = [edge[0] for edge in edge_path]
    # add last vertex of edge path only if not closed loop
    if edge_path[0][0] != edge_path[-1][-1]:
        vertex_path.append(edge_path[-1][-1])

    # store changes to make in the faces along the vertex path in the following format {face to change = [old vertex, new vertex]}
    to_change = {}

    # iterate along path
    for i, vkey in enumerate(vertex_path):
        # vertices before and after current
        last_vkey = vertex_path[i - 1]
        next_vkey = vertex_path[i + 1 - len(vertex_path)]

        # skip the extremities of the vertex path, except if the path is a loop or if vertex is on boundary
        if (edge_path[0][0] == edge_path[-1][-1]) or (i != 0 and i != len(vertex_path) - 1) or mesh.is_vertex_on_boundary(vkey):
            # duplicate vertex and its attributes
            attr = mesh.vertex[vkey]
            new_vkey = mesh.add_vertex(attr_dict = attr)
            duplicates.append([vkey, new_vkey])
            # split neighbours in two groups depending on the side of the path
            vertex_nbrs = mesh.vertex_neighbours(vkey, True)
            
            # two exceptions on last_vkey or next_vkey if the vertex is on the boundary or a non-manifold vertex in case of the last vertex of a closed edge path
            if edge_path[0][0] == edge_path[-1][-1] and i == len(vertex_path) - 1:
                next_vkey = vertex_path[0]
            if mesh.is_vertex_on_boundary(vkey):
                for j in range(len(vertex_nbrs)):
                    if mesh.is_vertex_on_boundary(vertex_nbrs[j - 1]) and mesh.is_vertex_on_boundary(vertex_nbrs[j]):
                        before, after = vertex_nbrs[j - 1], vertex_nbrs[j]
                if i == 0:
                    last_vkey = before
                elif i == len(vertex_path) - 1:
                    next_vkey = after

            idxa = vertex_nbrs.index(last_vkey)
            idxb = vertex_nbrs.index(next_vkey)
            if idxa < idxb:
                half_nbrs = vertex_nbrs[idxa : idxb]
            else:
                half_nbrs = vertex_nbrs[idxa :] + vertex_nbrs[: idxb]
            
            # get faces corresponding to vertex neighbours
            faces = [mesh.halfedge[nbr][vkey] for nbr in half_nbrs]
            # store change per face with index of duplicate vertex
            for fkey in faces:
                if fkey in to_change:
                    # add to other changes
                    to_change[fkey] += [[vkey, new_vkey]]
                else: 
                    to_change[fkey] = [[vkey, new_vkey]]

    # apply stored changes
    for fkey, changes in to_change.items():
        if fkey is None:
            continue
        face_vertices = mesh.face_vertices(fkey)[:]
        for change in changes:
            old_vertex, new_vertex = change
            # replace in list of face vertices
            idx = face_vertices.index(old_vertex)
            face_vertices[idx] = new_vertex
        # modify face by removing it and adding the new one
        attr = mesh.facedata[fkey]
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey, attr_dict = attr)

    return duplicates

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
    