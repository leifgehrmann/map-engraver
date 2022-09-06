from typing import Union, List

from shapely.geometry import MultiPolygon,\
    GeometryCollection,\
    Polygon,\
    MultiLineString,\
    LineString


def geoms_to_multi_polygon(
        geoms: Union[Polygon, MultiPolygon, GeometryCollection]
) -> MultiPolygon:
    new_polygons: List[Polygon] = []
    if isinstance(geoms, GeometryCollection):
        for inner_geom in geoms.geoms:
            if isinstance(inner_geom, MultiPolygon):
                new_polygons.extend(inner_geom.geoms)
            elif isinstance(inner_geom, Polygon) and not inner_geom.is_empty:
                new_polygons.append(inner_geom)
    elif isinstance(geoms, MultiPolygon):
        return geoms
    elif isinstance(geoms, Polygon) and not geoms.is_empty:
        new_polygons.append(geoms)

    return MultiPolygon(new_polygons)


def geoms_to_multi_line_string(
        geoms: Union[LineString, MultiLineString, GeometryCollection]
) -> MultiLineString:
    new_line_strings: List[LineString] = []
    if isinstance(geoms, GeometryCollection):
        for inner_geom in geoms.geoms:
            if isinstance(inner_geom, MultiLineString):
                new_line_strings.extend(inner_geom.geoms)
            elif isinstance(inner_geom, LineString) and \
                    not inner_geom.is_empty:
                new_line_strings.append(inner_geom)
    elif isinstance(geoms, MultiLineString):
        return geoms
    elif isinstance(geoms, LineString) and not geoms.is_empty:
        new_line_strings.append(geoms)

    return MultiLineString(new_line_strings)
