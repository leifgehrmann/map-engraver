import math

from typing import Optional, Tuple

from pyproj import CRS
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import transform, unary_union

from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from map_engraver.data.osm_shapely_ops.homogenize import geoms_to_multi_polygon
from map_engraver.data.osm_shapely_ops.transform import \
    transform_interpolated_euclidean
from map_engraver.data.proj.masks import crs_mask, wgs84_mask


def canvas_mask(
        canvas_polygon: Polygon,
        transformers_builder: GeoCanvasTransformersBuilder
) -> MultiPolygon:
    """
    Returns a MultiPolygon that covers the extent of the CRS projection, and
    the extent of the canvas, in the canvas's coordinate space.

    In other words, it's the intersection of the canvas box and the extent of
    the CRS projection.

    For example, in the case of an orthographic globe projection that is
    centered in the middle of the canvas, it will simply return the extent of
    the globe projection.

    In another example, in the case of a zoomed in projection of the globe, it
    will simply return the extent of the canvas.

    :param canvas_polygon:
    :param transformers_builder:
    :return:
    """
    crs_polygon = crs_mask(transformers_builder.crs)
    if crs_polygon is None:
        return MultiPolygon([canvas_polygon])

    crs_polygon = crs_mask(transformers_builder.crs)
    transformers_builder = transformers_builder.copy()
    transformers_builder.set_data_crs(None)
    crs_to_canvas = transformers_builder.build_crs_to_canvas_transformer()
    crs_polygon = transform(crs_to_canvas, crs_polygon)
    return canvas_polygon.intersection(crs_polygon)


def canvas_crs_mask(
        canvas_polygon: Polygon,
        transformers_builder: GeoCanvasTransformersBuilder
) -> MultiPolygon:
    """
    Returns a MultiPolygon that covers the extent of the CRS projection and the
    extent of the canvas, in the CRS's own coordinate space.

    :param canvas_polygon:
    :param transformers_builder:
    :return:
    """
    transformers_builder = transformers_builder.copy()
    transformers_builder.set_data_crs(None)
    canvas_to_crs = transformers_builder.build_canvas_to_crs_transformer()
    canvas_polygon = transform(canvas_to_crs, canvas_polygon)

    crs_polygon = crs_mask(transformers_builder.crs)

    if crs_polygon is None:
        return MultiPolygon([canvas_polygon])

    return canvas_polygon.intersection(crs_polygon)


def canvas_wgs84_mask(
        canvas_polygon: Polygon,
        transformers_builder: GeoCanvasTransformersBuilder
) -> Optional[MultiPolygon]:
    """
    Returns a MultiPolygon that covers the extent of the CRS projection and the
    extent of the canvas, in the WGS-84 coordinate space.

    This is useful for culling datasets to fit within a canvas.

    :param canvas_polygon:
    :param transformers_builder:
    :return:
    """
    transformers_builder = transformers_builder.copy()
    transformers_builder.set_data_crs(CRS.from_epsg(4326))
    crs_to_canvas = transformers_builder.build_crs_to_canvas_transformer()
    canvas_to_crs = transformers_builder.build_canvas_to_crs_transformer()

    wgs84_polygons = wgs84_mask(transformers_builder.crs)

    if wgs84_polygons is None:
        return None

    # Split the WGS 84 MultiPolygon into two halves, a western hemisphere and
    # an eastern hemisphere. That way we can resolve polygons that are
    # accidentally placed on the prime meridian.
    w_polygon = Polygon([(90, -180), (90, 0), (-90, 0), (-90, -180)])
    e_polygon = Polygon([(90, 0), (90, 180), (-90, 180), (-90, 0)])
    w_wgs84_polygons = geoms_to_multi_polygon(
        wgs84_polygons.intersection(w_polygon)
    )
    e_wgs84_polygons = geoms_to_multi_polygon(
        wgs84_polygons.intersection(e_polygon)
    )

    # Transform the MultiPolygon from the WGS 84 projection to the canvas. This
    # can fail if interpolated points fall outside the CRS it is projecting to,
    # but in theory the wgs84_polygons should be designed to not contain such
    # interpolated points.
    w_wgs84_polygons = transform_interpolated_euclidean(
        crs_to_canvas,
        w_wgs84_polygons
    )
    e_wgs84_polygons = transform_interpolated_euclidean(
        crs_to_canvas,
        e_wgs84_polygons
    )

    # Doing a simple intersection of Polygons could result in non-area
    # geometries like Points and LineStrings being generated. We use
    # `geoms_to_multi_polygon` to make sure we exclude those geometries after
    # an intersection occurs.
    w_intersection_geoms = []
    e_intersection_geoms = []

    for wgs84_multi_polygon_sub_geom in w_wgs84_polygons.geoms:
        new_sub_geoms = geoms_to_multi_polygon(
            canvas_polygon.intersection(wgs84_multi_polygon_sub_geom)
        )
        for sub_geom in new_sub_geoms.geoms:
            w_intersection_geoms.append(sub_geom)
    for wgs84_multi_polygon_sub_geom in e_wgs84_polygons.geoms:
        new_sub_geoms = geoms_to_multi_polygon(
            canvas_polygon.intersection(wgs84_multi_polygon_sub_geom)
        )
        for sub_geom in new_sub_geoms.geoms:
            e_intersection_geoms.append(sub_geom)

    w_wgs84_polygons = MultiPolygon(w_intersection_geoms)
    e_wgs84_polygons = MultiPolygon(e_intersection_geoms)

    # Convert the canvas coordinates back to WGS 84.
    w_wgs84_polygons = transform_interpolated_euclidean(
        canvas_to_crs,
        w_wgs84_polygons
    )
    e_wgs84_polygons = transform_interpolated_euclidean(
        canvas_to_crs,
        e_wgs84_polygons
    )

    # In the process of transforming between WGS 84 and the CRS, we may have
    # transformed coordinates that sit on the prime-meridian on the wrong
    # hemisphere. This section is fix that by moving the coordinates for each
    # geom on the left and right side of the hemisphere.
    w_wgs84_polygons = transform(
        _fix_west_hemisphere_coord, w_wgs84_polygons
    )
    e_wgs84_polygons = transform(
        _fix_east_hemisphere_coord, e_wgs84_polygons
    )

    polygons_to_unionize = []
    if not w_wgs84_polygons.is_empty:
        polygons_to_unionize.append(w_wgs84_polygons)
    if not e_wgs84_polygons.is_empty:
        polygons_to_unionize.append(e_wgs84_polygons)

    wgs84_polygons = geoms_to_multi_polygon(
        unary_union(polygons_to_unionize)
    )

    return wgs84_polygons


def _fix_west_hemisphere_coord(x: float, y: float) -> Tuple[float, float]:
    if y > 90:
        return x, -180
    # Floating point calculation issues may occur, so we match coordinates
    # like -179.99999999999994 to -180 for clean shapes.
    if math.isclose(
            y,
            -180,
            rel_tol=0.000000000000001
    ):
        return x, -180
    return x, y


def _fix_east_hemisphere_coord(x: float, y: float) -> Tuple[float, float]:
    if y < -90:
        return x, 180
    # Floating point calculation issues may occur, so we match coordinates
    # like -179.99999999999994 to -180 for clean shapes.
    if math.isclose(
            y,
            180,
            rel_tol=0.000000000000001
    ):
        return x, 180
    return x, y
