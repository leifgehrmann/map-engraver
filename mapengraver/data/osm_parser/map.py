from pathlib import Path

from typing import Dict, List
import xml.etree.ElementTree as ElementTree

from . import Node
from . import Way
from . import Relation
from . import Parser


class Map:
    """A container for all parsed objects from an OSM file"""

    nodes: Dict[str, type(Node)]
    ways: Dict[str, type(Way)]
    relations: Dict[str, type(Relation)]

    def __init__(self):
        self.nodes = dict()
        self.ways = dict()
        self.relations = dict()

    @staticmethod
    def parse(self, osm_file: Path):
        tree = ElementTree.parse(osm_file.as_posix())
        root = tree.getroot()
        self.add(root)

    def add(self, osm_root: ElementTree):
        new_nodes = Parser.get_nodes(osm_root)
        new_ways = Parser.get_ways(osm_root)
        new_relations = Parser.get_relations(osm_root)

        self.nodes = {**self.nodes, **new_nodes}
        self.ways = {**self.ways, **new_ways}
        self.relations = {**self.relations, **new_relations}

    def get_node(self, ref: str) -> Node:
        return self.nodes[ref]

    def get_way(self, ref: str) -> Way:
        return self.ways[ref]

    def get_relation(self, ref: str) -> Relation:
        return self.relations[ref]

    def get_nodes_for_way(self, ref: str) -> List[Node]:
        if ref not in self.ways:
            print("Unknown Way id: " + str(ref) + " . Returning []")
            return []
        return [self.nodes[node_ref] for node_ref in self.ways[ref].node_refs]
