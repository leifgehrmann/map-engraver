from enum import Enum
from typing import Tuple

from shapely.geometry import \
    MultiPolygon, \
    Polygon, \
    LinearRing, \
    LineString, \
    GeometryCollection
from shapely.ops import unary_union

from map_engraver.data.osm import Osm
from map_engraver.data.osm.filter import filter_elements
from map_engraver.data.osm.util import get_nodes_for_way
from map_engraver.data.osm_shapely.piece_together_ways import \
    piece_together_ways
from map_engraver.data.osm_shapely_ops.homogenize import \
    geoms_to_multi_line_string, \
    geoms_to_multi_polygon


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
                   Note that incomplete ways must begin and terminate outside
                   the bounds for the algorithm to work.
    :param output_type: Specify whether to return a land or water MultiPolygon.
    :return: A MultiPolygon representing the coastline shape.
    """
    osm_coastline = filter_elements(
        osm,
        lambda _, way_element: (
                'natural' in way_element.tags and
                way_element.tags['natural'] == 'coastline'
        ),
        filter_nodes=False,
        filter_relations=False
    )

    if len(osm_coastline.ways) == 0:
        raise Exception(
            'Failed to generate coastline. One or more OSM ways with the tag '
            'natural=coastline are required.'
        )

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
        False
    )

    # Convert all complete_way_nodes to Polygons. Clockwise polygons are
    # considered land, counter-clockwise polygons are water.
    complete_land_polygons = []
    complete_water_polygons = []
    for ref, complete_way_nodes in complete_ways_nodes.items():
        coordinates = []
        for way_node in complete_way_nodes:
            coordinates.append((way_node.lat, way_node.lon))
        linear_ring = LinearRing(coordinates)
        if linear_ring.is_ccw:
            complete_water_polygons.append(
                Polygon(coordinates).intersection(bounds_polygon)
            )
        else:
            complete_land_polygons.append(
                Polygon(coordinates).intersection(bounds_polygon)
            )

    # Convert all incomplete ways to MultiLineStrings.
    incomplete_linear_strings = []
    for ref, incomplete_way_nodes in incomplete_ways_nodes.items():
        coordinates = []
        for way_node in incomplete_way_nodes:
            coordinates.append((way_node.lat, way_node.lon))
        linear_string = LineString(coordinates)
        incomplete_linear_strings.append(linear_string)
    incomplete_multi_line_strings = unary_union(incomplete_linear_strings)
    incomplete_multi_line_strings = geoms_to_multi_line_string(
        incomplete_multi_line_strings.intersection(bounds_polygon)
    )

    # Close all incomplete ways so they become Polygons.
    incomplete_polygons = []
    for incomplete_line_string in incomplete_multi_line_strings.geoms:
        # Todo:
        # print('-------------------------')
        # print(bounds)
        # print(start_coordinate[0], start_coordinate[1])
        # print(
        #     start_coordinate[0] == bounds[0],
        #     start_coordinate[1] == bounds[1]
        # )
        # print(
        #     start_coordinate[0] == bounds[2],
        #     start_coordinate[1] == bounds[3]
        # )
        # print(end_coordinate[0], end_coordinate[1])
        # print(
        #     end_coordinate[0] == bounds[0],
        #     end_coordinate[1] == bounds[1]
        # )
        # print(
        #     end_coordinate[0] == bounds[2],
        #     end_coordinate[1] == bounds[3]
        # )

        # We should now have a collection of incomplete ways that have start
        # and end points that intersect the bounds. We now want to connect the
        # end with the start to complete the shape so we can turn it into a
        # Polygon. From the end coordinate, which should lie on the bound, we
        # need to go counter-clockwise around the bounds until we reach the
        # Start.
        #
        # In the example below, the LineString going through the bounds begins
        # with 'S' and ends at 'E'. To complete the polygon, we loop through
        # each section, in this case starting at Section 4, connecting between
        # Section 1, and ending at Section 2, where the start point 'S'. The
        # resulting lines are represented a solid line. In total, 2 points are
        # added to the line_string to complete the shape.
        #
        #               Section 4
        #              <──────────
        #             ┌────────E ╴ ╴
        #           │ │ ╭──────╯   ' ^
        #           │ │ ╰──╮       ' │
        # Section 1 │ │   ╭╯╭─╮    ' │ Section 3
        #           │ │   ╰╮│ ╰╮   ' │
        #           V │    ╰╯  │   ' │
        #             └────────S ╴ '
        #              ──────────>
        #                Section 2

        new_coordinates = list(incomplete_line_string.coords)
        start_coordinate = new_coordinates[0]
        end_coordinate = new_coordinates[-1]
        sections_iterated = 0

        while end_coordinate != start_coordinate:
            # print(end_coordinate)  # Todo: remove when confident this works
            if sections_iterated == 5:
                # If this happens, we recommend either:
                # 1. Downloading the rest of the coastline from OpenStreetMap
                #    that are out of bounds.
                # 2. Manually updating the OSM file to move the terminating
                #    coordinate out of bounds.
                # 3. Removing the coastline altogether.
                raise Exception(
                    'Failed to generate coastline. An incomplete coastline '
                    'way starts with a point that is inside the bounds. '
                    'Incomplete coastlines must start and end with '
                    'coordinates outside of the bounds.'
                )
            # Section 1
            if (
                    end_coordinate[1] == bounds[1] and
                    end_coordinate[0] != bounds[0]
            ):
                # print('section 1')  # Todo: remove when confident this works
                if (
                        start_coordinate[1] == end_coordinate[1] and
                        start_coordinate[0] <= end_coordinate[0]
                ):
                    new_coordinate = start_coordinate
                else:
                    new_coordinate = (bounds[0], bounds[1])
            # Section 2
            elif (
                    end_coordinate[0] == bounds[0] and
                    end_coordinate[1] != bounds[3]
            ):
                # print('section 2')  # Todo: remove when confident this works
                if (
                        start_coordinate[0] == end_coordinate[0] and
                        start_coordinate[1] >= end_coordinate[1]
                ):
                    new_coordinate = start_coordinate
                else:
                    new_coordinate = (bounds[0], bounds[3])
            # Section 3
            elif (
                    end_coordinate[1] == bounds[3] and
                    end_coordinate[0] != bounds[2]
            ):
                # print('section 3')  # Todo: remove when confident this works
                if (
                        start_coordinate[1] == end_coordinate[1] and
                        start_coordinate[0] >= end_coordinate[0]
                ):
                    new_coordinate = start_coordinate
                else:
                    new_coordinate = (bounds[2], bounds[3])
            # Section 4
            elif (
                    end_coordinate[0] == bounds[2] and
                    end_coordinate[1] != bounds[1]
            ):
                # print('section 4')  # Todo: remove when confident this works
                if (
                        start_coordinate[0] == end_coordinate[0] and
                        start_coordinate[1] <= end_coordinate[1]
                ):
                    new_coordinate = start_coordinate
                else:
                    new_coordinate = (bounds[2], bounds[1])
            else:
                # If this happens, we recommend either:
                # 1. Downloading the rest of the coastline from OpenStreetMap
                #    that are out of bounds.
                # 2. Manually updating the OSM file to move the terminating
                #    coordinate out of bounds.
                # 3. Removing the coastline altogether.
                raise Exception(
                    'Failed to generate coastline. An incomplete coastline '
                    'way ends with a point that is inside the bounds. '
                    'Incomplete coastlines must start and end with '
                    'coordinates outside of the bounds.'
                )

            new_coordinates.append(new_coordinate)
            end_coordinate = new_coordinate
            sections_iterated += 1
        incomplete_polygons.append(Polygon(new_coordinates))

    # Start with the assumption that land will always be returned.
    composite_geom = GeometryCollection()

    # In theory, because the coastlines never overlap, it's possible to
    # determine using the incomplete polygons whether land should or should not
    # exist.
    # If two polygons intersect, that means the land is the intersection of the
    # two geoms. If they don't intersect, that means they are separate bodies
    # of land, and can therefore be merged.
    for incomplete_polygon in incomplete_polygons:
        if composite_geom.intersects(incomplete_polygon):
            composite_geom = composite_geom.intersection(
                incomplete_polygon
            )
        else:
            composite_geom = unary_union(
                [composite_geom, incomplete_polygon]
            )

    # Add the complete land shapes.
    if len(complete_land_polygons) > 0:
        for complete_land_polygon in complete_land_polygons:
            if composite_geom.contains(complete_land_polygon):
                raise NotImplementedError(
                    'Failed to generate coastline. The current algorithm does '
                    'not support nested coastlines more than 2 layers deep. '
                    'For now convert islands into multipolygons.'
                )
            composite_geom = unary_union(
                [composite_geom, complete_land_polygon]
            )

    # Fun edge case, if there are no incomplete coastlines and no land
    # polygons, but we have water polygons, we can assume that the bounds are
    # within land.
    if composite_geom.is_empty and len(complete_water_polygons) > 0:
        composite_geom = bounds_polygon

    # Subtract the complete water shapes.
    if len(complete_water_polygons) > 0:
        for complete_water_polygon in complete_water_polygons:
            if not composite_geom.contains(complete_water_polygon):
                raise NotImplementedError(
                    'Failed to generate coastline. The current algorithm does '
                    'not support nested coastlines more than 2 layers deep. '
                    'For now, convert lakes within islands into '
                    'multipolygons. If nested coastlines are not expected, '
                    'make sure to check the coastlines for ways that are '
                    'incorrectly oriented as clockwise.'
                )
            composite_geom = composite_geom.difference(
                complete_water_polygon
            )

    # To return the water instead of land, we simply perform a symmetric
    # difference of the land geom with the bounds polygon.
    if output_type == CoastlineOutputType.WATER:
        composite_geom = composite_geom.symmetric_difference(bounds_polygon)

    composite_multi_polygon = geoms_to_multi_polygon(composite_geom)

    # Todo: remove when confident this works
    # This is helpful for debugging the output.
    # Regex: (\d+) ([\d.]+) ([\d.]+)
    # geom_id = 0
    # for composite_polygon in composite_multi_polygon.geoms:
    #     geom_id += 1
    #     for composite_coord in composite_polygon.exterior.coords:
    #         print(geom_id, composite_coord[0], composite_coord[1])
    #     interior_geom_id = 1000 * geom_id
    #     for composite_interior in composite_polygon.interiors:
    #         interior_geom_id += 1
    #         for composite_interior_coord in composite_interior.coords:
    #             print(
    #                 interior_geom_id,
    #                 composite_interior_coord[0],
    #                 composite_interior_coord[1]
    #             )

    return composite_multi_polygon
