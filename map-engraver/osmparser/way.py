from typing import Dict, List
import xml.etree.ElementTree as ElementTree

import osmparser


class Way:
    """An OSM way"""
    id: str
    tags: Dict[str, str]
    node_refs: List[str]

    def __init__(self, osm_element):
        self.id = osm_element.attrib['id']
        self.tags = osmparser.Parser.get_element_tags(osm_element)
        self.node_refs = Way.get_way_node_refs(osm_element)
        self.nodes = None

    @staticmethod
    def get_way_node_refs(osm_element: ElementTree) -> List[str]:
        """Get all nodes for a way"""
        node_refs = list()
        for child in osm_element:
            if child.tag == 'nd':
                node_ref = str(child.attrib['ref'])
                node_refs.append(node_ref)
        return node_refs
