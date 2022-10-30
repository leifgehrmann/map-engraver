from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from typing import Optional, List, Dict, Callable, Union

from map_engraver.data.osm import Node
from map_engraver.data.osm import Way
from map_engraver.data.osm import Relation
from map_engraver.data.osm import MemberTypes
from map_engraver.data.osm import Osm
from map_engraver.data.osm.util import get_nodes_for_way
from map_engraver.data.osm_shapely.piece_together_ways import \
    piece_together_ways


class OsmToShapely:
    def __init__(
            self,
            osm: Osm
    ):
        """
        :param osm:
        """
        self.osm = osm
        self._incomplete_refs_handler = lambda element, refs: None

    @property
    def incomplete_refs_handler(self):
        return self._incomplete_refs_handler

    @incomplete_refs_handler.setter
    def incomplete_refs_handler(
            self,
            x: Callable[[Union[Way, Relation], List[str]], None]
    ):
        self._incomplete_refs_handler = x

    def node_to_point(
            self,
            node: Node
    ) -> Optional[Point]:
        return Point(node.lat, node.lon)

    def nodes_to_points(
            self,
            nodes: Dict[str, Node]
    ) -> Dict[str, Optional[Point]]:
        return {k: self.node_to_point(v) for k, v in nodes.items()}

    def way_to_line_string(
            self,
            way: Way
    ) -> Optional[LineString]:
        nodes = get_nodes_for_way(self.osm, way.id)
        line_string_array = []
        for node in nodes:
            line_string_array.append((node.lat, node.lon))
        return LineString(line_string_array)

    def ways_to_line_strings(
            self,
            ways: Dict[str, Way]
    ) -> Dict[str, Optional[LineString]]:
        return {k: self.way_to_line_string(v) for k, v in ways.items()}

    def way_to_polygon(
            self,
            way: Way
    ) -> Optional[Polygon]:
        nodes = get_nodes_for_way(self.osm, way.id)
        polygon_array = []
        for node in nodes:
            polygon_array.append((node.lat, node.lon))
        if polygon_array[len(polygon_array)-1] == polygon_array[0] and \
                len(polygon_array) > 2:
            p = Polygon(polygon_array)
            if p.exterior.is_ccw:
                p = Polygon(reversed(polygon_array))
            return p
        raise WayToPolygonError("Could not convert way to polygon: " + way.id)

    def ways_to_polygons(
            self,
            ways: Dict[str, Way]
    ) -> Dict[str, Optional[Polygon]]:
        return {k: self.way_to_polygon(v) for k, v in ways.items()}

    def relation_to_multi_polygon(
            self,
            relation: Relation
    ) -> Optional[MultiPolygon]:
        outer_way_refs = []
        outer_way_all_nodes = {}
        outer_way_start_nodes = {}
        outer_way_end_nodes = {}
        inner_way_refs = []
        inner_way_all_nodes = {}
        inner_way_start_node = {}
        inner_way_end_node = {}
        for member in relation.members:
            if member.type == MemberTypes.WAY:
                way_nodes = get_nodes_for_way(self.osm, member.ref)
                if len(way_nodes) == 0:
                    continue
                if member.role == "inner":
                    inner_way_all_nodes[member.ref] = way_nodes
                    inner_way_start_node[member.ref] = way_nodes[0]
                    inner_way_end_node[member.ref] = way_nodes[
                        len(inner_way_all_nodes[member.ref]) - 1
                    ]
                    inner_way_refs.append(member.ref)
                elif member.role == "outer":
                    outer_way_all_nodes[member.ref] = way_nodes
                    outer_way_start_nodes[member.ref] = way_nodes[0]
                    outer_way_end_nodes[member.ref] = way_nodes[
                        len(outer_way_all_nodes[member.ref]) - 1
                    ]
                    outer_way_refs.append(member.ref)

        # now piece together the outer way
        incomplete_ways_nodes, outer_ways_nodes = piece_together_ways(
            outer_way_refs,
            outer_way_all_nodes,
            outer_way_start_nodes,
            outer_way_end_nodes,
            True
        )

        # Fail completely if there are any instances of incomplete_way_refs
        # for the exterior polygon, meaning we failed to piece together the
        # exterior ways. We fail completely because it's very likely that
        # interior ways will intersect with the incomplete exterior ways.
        # This happens a lot with buildings which have holes in them.
        if len(incomplete_ways_nodes) > 0:
            self.incomplete_refs_handler(
                relation,
                incomplete_ways_nodes.keys()
            )
            return None

        # Fail completely if we somehow get no nodes pieced together.
        if 0 == len(outer_ways_nodes):
            self.incomplete_refs_handler(relation, [])
            return None

        # create exteriors of polygons
        exterior_polygons = []
        for outer_way_nodes in outer_ways_nodes.values():
            exterior_nodes = []
            for node in outer_way_nodes:
                exterior_nodes.append((node.lat, node.lon))
            exterior_polygon = Polygon(exterior_nodes)
            if exterior_polygon.exterior.is_ccw:
                exterior_polygon = Polygon(reversed(exterior_nodes))
            exterior_polygons.append(exterior_polygon)

        # now piece together the inner way
        incomplete_ways_nodes, inner_ways_nodes = piece_together_ways(
            inner_way_refs,
            inner_way_all_nodes,
            inner_way_start_node,
            inner_way_end_node,
            True
        )

        if len(incomplete_ways_nodes) > 0:
            # Failed to piece together interior way.
            # Continuing as normal, but the shape might look wrong...
            self.incomplete_refs_handler(
                relation,
                incomplete_ways_nodes.keys()
            )

        exterior_polygons_interiors = [
            [] for _ in range(len(exterior_polygons))
        ]
        for inner_way_nodes in inner_ways_nodes.values():
            interior_coordinates = []
            for node in inner_way_nodes:
                interior_coordinates.append((node.lat, node.lon))
            interior_polygon = Polygon(interior_coordinates)
            if not interior_polygon.exterior.is_ccw:
                interior_coordinates = list(reversed(interior_coordinates))

            for e_p in range(len(exterior_polygons)):
                if exterior_polygons[e_p].intersects(interior_polygon):
                    exterior_polygons_interiors[e_p].append(
                        interior_coordinates
                    )

        # Finally, combine the exterior_polygons with the interiors
        geoms = []
        for e_p in range(len(exterior_polygons)):
            geoms.append((
                exterior_polygons[e_p].exterior.coords,
                exterior_polygons_interiors[e_p]
            ))

        return MultiPolygon(geoms)

    def relations_to_multi_polygons(
            self,
            relations: Dict[str, Relation]
    ) -> Dict[str, Optional[MultiPolygon]]:
        return {
            k: self.relation_to_multi_polygon(v) for k, v in relations.items()
        }


class WayToPolygonError(Exception):
    pass
