from shapely.geometry import MultiPolygon
from typing import Optional

from pyproj import CRS

from map_engraver.data.proj.azimuthal_masks import \
    is_supported_azimuthal_projection, \
    azimuthal_mask, \
    azimuthal_mask_wgs84
from map_engraver.data.proj.cylindrical_masks import \
    is_supported_cylindrical_projection, \
    cylindrical_mask, \
    cylindrical_mask_wgs84
from map_engraver.data.proj.wgs84_masks import \
    wgs84_mask as wgs84_mask_gen


def crs_mask(crs: CRS) -> Optional[MultiPolygon]:
    """
    Returns a mask that can be used to clip shapely objects in the CRS's
    projection.

    This can be used to create a backdrop polygon. For example, with the
    orthographic projection, the globe's extent can be displayed.

    :param crs:
    :return:
    """
    if crs.name == 'WGS 84':
        return MultiPolygon([wgs84_mask_gen()])
    if is_supported_azimuthal_projection(crs):
        return MultiPolygon([azimuthal_mask(crs)])
    if is_supported_cylindrical_projection(crs):
        return cylindrical_mask(crs)
    return None
    pass


def wgs84_mask(crs: CRS) -> Optional[MultiPolygon]:
    """
    Returns a mask that can be used to clip shapely objects in the WGS 84
    projection, so they can be transformed into the CRS.

    :param crs:
    :return:
    """
    if crs.name == 'WGS 84':
        return MultiPolygon([wgs84_mask_gen()])
    if is_supported_azimuthal_projection(crs):
        return azimuthal_mask_wgs84(crs)
    if is_supported_cylindrical_projection(crs):
        return cylindrical_mask_wgs84(crs)
    return None
