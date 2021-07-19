from typing import Dict

from mapengraver.data.osm import Node, Way, Relation


class OsmSubset:
    """A collection of OSM elements being a subset of an Osm object"""

    nodes: Dict[str, Node]
    ways: Dict[str, Way]
    relations: Dict[str, Relation]

    def __init__(
            self,
            nodes: Dict[str, Node],
            ways: Dict[str, Way],
            relations: Dict[str, Relation]
    ):
        self.nodes = nodes
        self.ways = ways
        self.relations = relations
