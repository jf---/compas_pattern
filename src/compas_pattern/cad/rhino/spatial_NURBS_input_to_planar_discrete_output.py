try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas_rhino.geometry.surface import RhinoSurface

import compas_rhino as rhino

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'surface_borders',
    'spatial_NURBS_input_to_planar_discrete_output',
]

# extension to compas_rhino.geometry.RhinoSurface.borders with border type
def surface_borders(surface, border_type = 0):
        border = rs.DuplicateSurfaceBorder(surface, border_type)
        curves = rs.ExplodeCurves(border, delete_input = True)
        return curves

def spatial_NURBS_input_to_planar_discrete_output(discretization_spacing, surface_guid, curve_features_guids = [], point_features_guids = []):
    """Creates planar polylines from the boundaries of a NURBS surface, NURBS curves and point on the NURBS surface
    by using the UV parameterisation with a user-input discretisation spacing.

    Parameters
    ----------
    discretization_spacing: real
        Spacing value for discretisation of NURBS surface borders and curves into polylines.
    surface: Rhino surface guid
        Untrimmed or trimmed Rhino NURBS surface.
    curve_features: Rhino curve guid
        Rhino NURBS curve on the surface.
    point_features: Rhino point guid
        Rhino point on the surface.

    Returns
    -------
    output: list
        Planar parameterised geometrical output: boundary, holes, polyline features and point features.

    Raises
    ------
    -

    """
    
    boundaries = surface_borders(surface_guid, border_type = 1)

    #if len(boundaries) > 1:
    #    boundaries = rs.JoinCurves(boundaries, delete_input = True)
    boundary_polylines = [curve_to_polyline(boundary, discretization_spacing) for boundary in boundaries]
    #boundary_polyline = rs.ConvertCurveToPolyline(boundaries[0], angle_tolerance = 45.0, tolerance = discretization_spacing, delete_input = True, min_edge_length = 0.9 * discretization_spacing, max_edge_length = 1.1 * discretization_spacing)
    uv_boundary_polylines = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(boundary_polyline)] for boundary_polyline in boundary_polylines]
    planar_boundary_polylines = [[[u, v, 0] for u, v in uv_boundary_polyline] for uv_boundary_polyline in uv_boundary_polylines]
    planar_boundary_polyline = []
    for polyline in planar_boundary_polylines:
        planar_boundary_polyline += polyline[: -1]
    planar_boundary_polyline.append(planar_boundary_polyline[0])
    rs.DeleteObjects(boundaries)
    rs.DeleteObjects(boundary_polylines)

    holes = surface_borders(surface_guid, border_type = 2)
    if len(holes) > 1:
        holes = rs.JoinCurves(holes, delete_input = True)
    hole_polylines = [curve_to_polyline(hole, discretization_spacing) for hole in holes]
    #hole_polylines = [rs.ConvertCurveToPolyline(hole, angle_tolerance = 45.0, tolerance = discretization_spacing, delete_input = True, min_edge_length = 0.9 * discretization_spacing, max_edge_length = 1.1 * discretization_spacing) for hole in holes]
    uv_hole_polylines = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(hole_polyline)] for hole_polyline in hole_polylines]
    planar_hole_polylines = [[[u, v, 0] for u, v in hole] for hole in uv_hole_polylines]
    rs.DeleteObjects(holes)
    rs.DeleteObjects(hole_polylines)

    polyline_features = [curve_to_polyline(curve_features_guid, discretization_spacing) for curve_features_guid in curve_features_guids]
    #polyline_features = [rs.ConvertCurveToPolyline(curve_features_guid, angle_tolerance = 45.0, tolerance = discretization_spacing, delete_input = True, min_edge_length = 0.9 * discretization_spacing, max_edge_length = 1.1 * discretization_spacing) for curve_features_guid in curve_features_guids]
    uv_polyline_features = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(polyline_feature)] for polyline_feature in polyline_features]
    planar_polyline_features = [[[u, v, 0] for u, v in feature] for feature in uv_polyline_features]
    rs.DeleteObjects(polyline_features)

    uv_point_features = [rs.SurfaceClosestPoint(surface_guid, point) for point in point_features_guids]
    planar_point_features = [[u, v, 0] for u, v in uv_point_features]

    return planar_boundary_polyline, planar_hole_polylines, planar_polyline_features, planar_point_features

def curve_to_polyline(curve_guid, discretization_spacing):
    n = int(rs.CurveLength(curve_guid) / discretization_spacing) + 1
    points = rs.DivideCurve(curve_guid, n)
    if rs.IsCurveClosed(curve_guid):
        points.append(points[0])
    return rs.AddPolyline(points)

def mapping_point_to_surface(point, surface_guid):
    """Maps a point in the plan on a spatial surface based on its parameterisation.
    [u, v, 0] -> [x, y, z]

    Parameters
    ----------
    point: list
        Coordinates of a point in the plane [x, y, 0].
    surface: Rhino surface guid
        Untrimmed or trimmed Rhino NURBS surface on which to map the point.

    Returns
    -------
    point_on_surface: list, None
        Coordinates of the point on the surface [u, v] -> [x, y, z].
        None if the point is not in the plane.

    Raises
    ------
    -

    """
    
    x, y, z = point

    if z != 0:
        return None

    point_on_surface = rs.EvaluateSurface(surface_guid, x, y)

    return point_on_surface

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
