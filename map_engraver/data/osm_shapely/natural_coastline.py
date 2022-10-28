from enum import Enum
from typing import Tuple

from shapely.geometry import MultiPolygon, Polygon, LinearRing, LineString
from shapely.ops import cascaded_union

from map_engraver.data.osm import Osm
from map_engraver.data.osm.filter import filter_elements
from map_engraver.data.osm.util import get_nodes_for_way
from map_engraver.data.osm_shapely.piece_together_ways import piece_together_ways
from map_engraver.data.osm_shapely_ops.homogenize import geoms_to_multi_line_string


class CoastlineOutputType(Enum):
    LAND = 1
    WATER = 2


def natural_coastline_to_multi_polygon(
        osm: Osm,
        bounds: Tuple[float, float, float, float],
        output_type: CoastlineOutputType
) -> MultiPolygon:
    """
    Returns a MultiPolygon that represents the land contained within the
    coastline. Only ways that have the tag natural=coastline are included.

    In OpenStreetMap, coastlines are built up by a sequence of way elements
    that span whole continents, but are regularly split in between to avoid
    editors from needing to download massive objects. They are similar to
    multipolygon relation elements, in that they have an outer and inner role,
    but instead the roles are expressed as way directions. For example, to draw
    a landmass, the way's nodes should be ordered counter-clock-wise.

    Warning: If no `natural=coastline` ways are found, an error will be raised.

    :param osm: The parsed OSM file containing the coastline ways.
    :param bounds: The size the polygon should be generated for.
    :param output_type: Specify whether to return land or water polygons.
    :return:
    """
    osm_coastline = filter_elements(
        osm,
        lambda _, way: (
                'natural' in way.tags and
                way.tags['natural'] == 'coastline'
        ),
        filter_nodes=False,
        filter_relations=False
    )

    if len(osm_coastline.ways) == 0:
        raise Exception('Failed to generate coastline. One or more OSM ways'
                        'with the tag natural=coastline are required.')

    bounds_polygon = Polygon([
        (bounds[0], bounds[1]),
        (bounds[0], bounds[3]),
        (bounds[2], bounds[3]),
        (bounds[2], bounds[1])
    ])

    way_refs = []
    way_all_nodes = {}
    way_start_nodes = {}
    way_end_nodes = {}

    for ref, way in osm_coastline.ways.items():
        way_nodes = get_nodes_for_way(osm, ref)
        way_all_nodes[ref] = way_nodes
        way_start_nodes[ref] = way_nodes[0]
        way_end_nodes[ref] = way_nodes[
            len(way_all_nodes[ref]) - 1
            ]
        way_refs.append(ref)

    incomplete_ways_nodes, complete_ways_nodes = piece_together_ways(
        way_refs,
        way_all_nodes,
        way_start_nodes,
        way_end_nodes,
    )

    # Convert all complete_way_nodes to Polygons. Clock-wise Todo
    complete_cw_polygons = []
    complete_ccw_polygons = []
    for ref, complete_way_nodes in complete_ways_nodes.items():
        coordinates = []
        for way_node in complete_way_nodes:
            coordinates.append((way_node.lat, way_node.lon))
        linear_ring = LinearRing(coordinates)
        if linear_ring.is_ccw:
            complete_ccw_polygons.append(Polygon(coordinates))
        else:
            complete_cw_polygons.append(
                bounds_polygon.difference(Polygon(coordinates))
            )

    incomplete_linear_strings = []
    for ref, incomplete_way_nodes in incomplete_ways_nodes.items():
        coordinates = []
        for way_node in incomplete_way_nodes:
            coordinates.append((way_node.lat, way_node.lon))
        linear_string = LineString(coordinates)
        incomplete_linear_strings.append(linear_string)

    incomplete_multi_line_strings = cascaded_union(incomplete_linear_strings)
    incomplete_multi_line_strings = geoms_to_multi_line_string(
        incomplete_multi_line_strings.intersection(bounds_polygon)
    )
    complete_polygons = []
    for incomplete_line_string in incomplete_multi_line_strings.geoms:
        print(incomplete_line_string)

    # Todo

