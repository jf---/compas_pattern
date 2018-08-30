from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'weld_mesh',
    'join_mesh',
    'join_and_weld_meshes',
]

def weld_mesh(mesh, precision = '3f'):
    """Welds vertices of a mesh within some precision.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    precision: str
        Float precision of the geometric_key.

    Returns
    -------
    vertices : list
        The coordinates of the vertices after welding.
    face_vertices : list
        The vertices of the faces after welding.

    Raises
    ------
    -

    """
    
    vertices = []
    face_vertices = []
    vertex_map = {}
    count = 0

    # store vertices from different geometric key only
    for vkey in mesh.vertices():
        xyz = mesh.vertex_coordinates(vkey)
        geom_key = geometric_key(xyz, precision)
        if geom_key not in vertex_map:
            vertex_map[geom_key] = count
            vertices.append(xyz)
            count += 1

    # update face vertices with index matching geometric key
    for fkey in mesh.faces():
            new_face_vertices = []
            for vkey in mesh.face_vertices(fkey):
                xyz = geometric_key(mesh.vertex_coordinates(vkey), precision)
                new_face_vertices.append(vertex_map[xyz])
            cleaned_face_vertices = []
            # remove consecutive duplicates
            for i, vkey in enumerate(new_face_vertices):
                if vkey != new_face_vertices[i - 1]:
                    cleaned_face_vertices.append(vkey)

    return vertices, face_vertices

def join_and_weld_meshes(meshes, precision = '3f'):
    """Joins and welds vertices of meshes within some precision.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    precision: str
        Float precision of the geometric_key.

    Returns
    -------
    vertices : list
        The coordinates of the vertices after joining and welding.
    face_vertices : list
        The vertices of the faces after joining and welding.

    Raises
    ------
    -

    """

    vertices = []
    face_vertices = []
    vertex_map = {}
    count = 0

    # store vertices from different geometric key only
    for mesh in meshes:
        for vkey in mesh.vertices():
            xyz = mesh.vertex_coordinates(vkey)
            geom_key = geometric_key(xyz, precision)
            if geom_key not in vertex_map:
                vertex_map[geom_key] = count
                vertices.append(xyz)
                count += 1

        # update face vertices with index matching geometric key
        for fkey in mesh.faces():
            new_face_vertices = []
            for vkey in mesh.face_vertices(fkey):
                xyz = geometric_key(mesh.vertex_coordinates(vkey), precision)
                new_face_vertices.append(vertex_map[xyz])
            cleaned_face_vertices = []
            # remove consecutive duplicates
            for i, vkey in enumerate(new_face_vertices):
                if vkey != new_face_vertices[i - 1]:
                    cleaned_face_vertices.append(vkey)

            face_vertices.append(new_face_vertices)

    return vertices, face_vertices

def join_meshes(meshes):
    """Joins meshes without welding.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    Returns
    -------
    vertices : list
        The coordinates of the vertices after joining.
    face_vertices : list
        The vertices of the faces after joining.

    Raises
    ------
    -

    """

    vertices = []
    face_vertices = []

    # procede per mesh
    for mesh in meshes:
        # aggregate vertices
        remap_vertices = {}
        for vkey in mesh.vertices():
            idx = len(vertices)
            remap_vertices[vkey] = idx
            vertices.append(mesh.vertex_coordinates(vkey))
        for fkey in mesh.faces():
            face_vertices.append([remap_vertices[vkey] for vkey in mesh.face_vertices(fkey)])

    return vertices, face_vertices

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas