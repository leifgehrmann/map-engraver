from abc import ABC

from shapely.geometry import Polygon, LineString
from typing import Optional, List, Tuple, Dict, Callable, Union

from mapengraver.data.osm import Node
from mapengraver.data.osm import Way
from mapengraver.data.osm import Relation
from mapengraver.data.osm import MemberTypes
from mapengraver.data.osm import Osm


class OsmLineString(LineString, ABC):
    def __init__(self, coordinates=None):
        super().__init__(coordinates)
        self._osm_tags = {}

    @property
    def osm_tags(self):
        return self._osm_tags

    @osm_tags.setter
    def osm_tags(self, x: Dict[str, str]):
        self._osm_tags = x


class OsmPolygon(Polygon, ABC):
    def __init__(self, shell=None, holes=None):
        super().__init__(shell, holes)
        self._osm_tags = {}

    @property
    def osm_tags(self):
        return self._osm_tags

    @osm_tags.setter
    def osm_tags(self, x: Dict[str, str]):
        self._osm_tags = x


class OsmToShapely:
    def __init__(
            self,
            osm: Osm,
            transform: Optional[Callable[
                [float, float],
                Tuple[float, float]
            ]] = None
    ):
        self.osm = osm
        if transform is None:
            self.transform = lambda x, y: (x, y)
        else:
            self.transform = transform

    def way_to_linestring(
            self,
            way: Way
    ) -> Optional[OsmLineString]:
        nodes = self.osm.get_nodes_for_way(way.id)
        linestring_array = []
        for node in nodes:
            linestring_array.append(self.transform(node.lon, node.lat))
        line_string = OsmLineString(linestring_array)
        line_string.osm_tags = way.tags
        return line_string

    def way_to_polygon(
            self,
            way: Way
    ) -> Optional[OsmPolygon]:
        nodes = self.osm.get_nodes_for_way(way.id)
        polygon_array = []
        for node in nodes:
            polygon_array.append(self.transform(node.lon, node.lat))
        if polygon_array[len(polygon_array)-1] == polygon_array[0] and len(polygon_array) > 2:
            p = OsmPolygon(polygon_array)
            if p.exterior.is_ccw:
                p = OsmPolygon(reversed(polygon_array))
            p.osm_tags = way.tags
            return p
        raise WayToPolygonError("Could not convert way to polygon: " + way.id)

    def _piece_together_ways(
            self,
            way_refs: List[str],
            way_nodes: Dict[str, List[Node]],
            way_start_nodes: Dict[str, Node],
            way_end_nodes: Dict[str, Node]
    ) -> Tuple[List[str], List[List[Node]]]:

        output_ways = []
        way_ref_index_1 = 0
        while way_ref_index_1 < len(way_refs):
            # print("----")
            way_ref_1 = way_refs[way_ref_index_1]
            # print("ref1 " + str(way_ref_1))

            # way is closed, so delete this way from the list of ways to process and continue to the next way
            if way_end_nodes[way_ref_1] == way_start_nodes[way_ref_1]:
                # print("Closed way!", way_end_nodes[way_ref_1], way_start_nodes[way_ref_1])
                output_ways.append(way_nodes[way_ref_1])

                del way_refs[way_ref_index_1]
                del way_nodes[way_ref_1]
                del way_start_nodes[way_ref_1]
                del way_end_nodes[way_ref_1]
                continue

            # go through all other ways (excluding self)
            way_ref_index_2 = 0
            while way_ref_index_2 < len(way_refs):
                way_ref_2 = way_refs[way_ref_index_2]
                if way_ref_1 == way_ref_2:
                    way_ref_index_2 += 1
                    continue

                # print("ref2 " + str(way_ref_2))

                # if the end node of the current way is connected to the start node of the other way
                if way_end_nodes[way_ref_1] == way_start_nodes[way_ref_2]:
                    # remove the first node of the other way to ensure we don't have redundant nodes and add it to the
                    # end of the current way
                    way_nodes_2 = way_nodes[way_ref_2][1:]
                    way_nodes[way_ref_1].extend(way_nodes_2)

                    # updated the linked list attributes
                    way_end_nodes[way_ref_1] = way_end_nodes[way_ref_2]

                    # Delete any mention of this way entirely!
                    del way_nodes[way_ref_2]
                    del way_start_nodes[way_ref_2]
                    del way_end_nodes[way_ref_2]
                    del way_refs[way_ref_index_2]
                    # if the index of the other way is behind the current way index, make sure to change the index
                    # because the other way was removed from the list!
                    way_ref_index_2 -= 1
                    if way_ref_index_1 > way_ref_index_2:
                        way_ref_index_1 -= 1

                    # Break out of this loop. The current way should be reprocessed in an attempt to discover
                    # more ways to connect / discover that it is a closed loop
                    break

                # otherwise proceed to the next way in the list
                way_ref_index_2 += 1

            # Only proceed onto the next item if we have properly gone through all the other ways
            if way_ref_index_2 == len(way_refs):
                way_ref_index_1 += 1

        return way_refs, output_ways

    def relation_to_polygon(
            self,
            relation: Relation
    ) -> Optional[OsmPolygon]:
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
                way_nodes = self.osm.get_nodes_for_way(member.ref)
                if len(way_nodes) == 0:
                    continue
                if member.role == "inner":
                    inner_way_all_nodes[member.ref] = way_nodes
                    inner_way_start_node[member.ref] = way_nodes[0]
                    inner_way_end_node[member.ref] = way_nodes[len(inner_way_all_nodes[member.ref]) - 1]
                    inner_way_refs.append(member.ref)
                elif member.role == "outer":
                    outer_way_all_nodes[member.ref] = way_nodes
                    outer_way_start_nodes[member.ref] = way_nodes[0]
                    outer_way_end_nodes[member.ref] = way_nodes[len(outer_way_all_nodes[member.ref]) - 1]
                    outer_way_refs.append(member.ref)

        # now piece together the outer way
        incomplete_way_refs, outer_ways_nodes = self._piece_together_ways(
            outer_way_refs,
            outer_way_all_nodes,
            outer_way_start_nodes,
            outer_way_end_nodes
        )

        # fail completely if there are
        if len(incomplete_way_refs) > 0:
            for member in relation.members:
                if member.type == MemberTypes.WAY:
                    test_way_nodes = self.osm.get_nodes_for_way(member.ref)
                    if member.role == "outer":
                        print("Relation Members for id: " + str(member.ref), test_way_nodes)
            print("Relation Id: " + str(relation.id))
            print("Failed to piece together exterior way. This is bad! FIX THIS!")
            print(incomplete_way_refs)
            return None

        if 0 == len(outer_ways_nodes) or len(outer_ways_nodes) > 1:
            print("Did not expect " + str(len(outer_ways_nodes)) + " exterior ways! This is bad! FIX THIS!")
            print("Relation Id: " + str(relation.id))
            print(incomplete_way_refs)
            return None

        # create exterior of polygon
        exterior = []
        for node in outer_ways_nodes[0]:
            exterior.append(self.transform(node.lon, node.lat))

        # now piece together the inner way
        incomplete_way_refs, inner_ways_nodes = self._piece_together_ways(
            inner_way_refs,
            inner_way_all_nodes,
            inner_way_start_node,
            inner_way_end_node
        )

        if len(incomplete_way_refs) > 0:
            print("Failed to piece together interior way. Continuing as normal, but something might look wrong...")
            print(incomplete_way_refs)

        interiors = []
        for inner_way_nodes in inner_ways_nodes:
            interior_coordinates = []
            for node in inner_way_nodes:
                interior_coordinates.append((node.lon, node.lat))
            interior_polygon = Polygon(interior_coordinates)
            if not interior_polygon.exterior.is_ccw:
                interior_coordinates = list(reversed(interior_coordinates))
            interiors.append(interior_coordinates)

        polygon = OsmPolygon(exterior, interiors)
        if polygon.exterior.is_ccw:
            polygon = OsmPolygon(reversed(exterior), interiors)
        polygon.osm_tags = relation.tags
        return polygon


class WayToPolygonError(Exception):
    pass


class WayToLineStringError(Exception):
    pass
