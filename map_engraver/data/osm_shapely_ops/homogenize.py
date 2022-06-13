from typing import Union, List

from shapely.geometry import MultiPolygon, GeometryCollection, Polygon


def geoms_to_multi_polygon(
        geoms: Union[Polygon, MultiPolygon, GeometryCollection]
) -> MultiPolygon:
    new_polygons: List[Polygon] = []
    if isinstance(geoms, GeometryCollection):
        for inner_geom in geoms.geoms:
            if isinstance(inner_geom, MultiPolygon):
                new_polygons.extend(inner_geom.geoms)
            elif isinstance(inner_geom, Polygon):
                new_polygons.append(inner_geom)
    elif isinstance(geoms, MultiPolygon):
        return geoms
    elif isinstance(geoms, Polygon):
        new_polygons.append(geoms)

    return MultiPolygon(new_polygons)
