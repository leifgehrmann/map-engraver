from typing import Optional

import re

from pyproj import CRS
from shapely.affinity import translate
from shapely.geometry import MultiPolygon, Point, Polygon

from map_engraver.data.osm_shapely_ops.homogenize import geoms_to_multi_polygon
from map_engraver.data.proj.wgs84_masks import wgs84_mask


def is_supported_cylindrical_projection(crs: CRS) -> bool:
    """
    :param crs:
    :return: Whether the projection is supported for `cylindrical_mask` and
             `cylindrical_mask_wgs84`.
    """
    if crs.coordinate_operation is None:
        return False
    if crs.coordinate_operation.name.startswith('UTM zone '):
        return True
    return False


def cylindrical_mask(
        crs: CRS,
        resolution=64,
        threshold=1
) -> Optional[MultiPolygon]:
    """
    :param crs:
    :param resolution:
    :param threshold:
    :return:
    """
    # If the projection is Universal Transverse Mercator, return None because
    # it appears the domain is (almost) infinite in all directions.
    if crs.coordinate_operation is not None and \
            crs.coordinate_operation.name.startswith('UTM zone '):
        return None
    raise RuntimeError(
        'Cannot generate mask for CRS: ' + crs.name
    )


def cylindrical_mask_wgs84(
        crs: CRS,
) -> MultiPolygon:
    """
    :param crs:
    :return:
    """
    # If the projection is Universal Transverse Mercator...
    if crs.coordinate_operation is not None and \
            crs.coordinate_operation.name.startswith('UTM zone '):
        # Get the UTM Zone position
        zone_regex = "UTM zone ([0-9]+)[NS]"
        match = re.match(zone_regex, crs.coordinate_operation.name)

        zone = int(match.group(1))

        # Calculate the "dead-spots" that exist in the UTM zones. These happen
        # to be circles that exist 90 degrees east and west of the UTM zone
        # along the equator. The circles are roughly 9 degrees in radius, both
        # on the latitude and longitude axis.
        lon1 = (-3 + zone * 6 - 90) - 360
        lon2 = (-3 + zone * 6 + 90) - 360
        left_circle = Point(0, 0).buffer(10.0)
        right_circle = Point(0, 0).buffer(10.0)
        left_circle = translate(left_circle, yoff=lon1)
        right_circle = translate(right_circle, yoff=lon2)

        mask = wgs84_mask()

        # Subtract the circles from the WGS 84 mask. For "dead-spots" that
        # exist on the prime-meridian we need to subtract them twice.
        mask = mask.difference(left_circle)
        left_circle = translate(left_circle, yoff=360)
        mask = mask.difference(left_circle)
        mask = mask.difference(right_circle)
        right_circle = translate(right_circle, yoff=360)
        mask = mask.difference(right_circle)

        # We also need to account for the top and bottom edges of the map. We
        # handle this lazily by subtracting a thin slice on the 0-degree
        # latitude between the right circle and the left circle.
        mask = mask.difference(Polygon([
            (0.000001, lon1),
            (0.000001, lon2),
            (-0.000001, lon2),
            (-0.000001, lon1),
        ]))
        mask = mask.difference(Polygon([
            (0.000001, lon1 + 360),
            (0.000001, lon2 + 360),
            (-0.000001, lon2 + 360),
            (-0.000001, lon1 + 360),
        ]))

        return geoms_to_multi_polygon(mask)
    else:
        raise RuntimeError(
            'Cannot generate WGS 84 mask for CRS: ' + crs.name
        )
