from typing import List

from pyproj import proj, Transformer

from map_engraver.transformers.geo_coordinate import GeoCoordinate


def transform_geo_coordinate_to_new_crs(
        geo_coordinate: GeoCoordinate,
        new_crs: proj.CRS
) -> GeoCoordinate:
    result = Transformer.from_proj(
        geo_coordinate.crs,
        new_crs
    ).transform(*geo_coordinate.tuple)
    return GeoCoordinate(result[0], result[1], new_crs)


def transform_geo_coordinates_to_new_crs(
        geo_coordinates: List[GeoCoordinate],
        new_crs: proj.CRS
) -> List[GeoCoordinate]:
    def transform_func(a):
        return transform_geo_coordinate_to_new_crs(a, new_crs)
    return list(map(transform_func, geo_coordinates))
