from typing import Dict, List

from . import Node
from . import Way
from . import Relation


class Osm:
    """A container for all objects from an OSM file"""

    nodes: Dict[str, type(Node)]
    ways: Dict[str, type(Way)]
    relations: Dict[str, type(Relation)]

    def __init__(
            self,
            nodes: Dict[str, type(Node)],
            ways: Dict[str, type(Way)],
            relations: Dict[str, type(Relation)]
    ):
        self.nodes = nodes
        self.ways = ways
        self.relations = relations

    def get_node(self, ref: str) -> Node:
        return self.nodes[ref]

    def get_way(self, ref: str) -> Way:
        return self.ways[ref]

    def get_relation(self, ref: str) -> Relation:
        return self.relations[ref]

    def get_nodes_for_way(self, ref: str) -> List[Node]:
        return [self.nodes[node_ref] for node_ref in self.ways[ref].node_refs]
