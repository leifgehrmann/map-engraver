from typing import List
import xml.etree.ElementTree as ElementTree

from mapengraver.data.osm import Element


class Way(Element):
    """An OSM way"""
    node_refs: List[str]

    def __init__(self, osm_element):
        super().__init__(osm_element)
        self.node_refs = Way._get_way_node_refs(osm_element)
        self.nodes = None

    @staticmethod
    def _get_way_node_refs(osm_element: ElementTree) -> List[str]:
        """Get all nodes for a way"""
        node_refs = list()
        for child in osm_element:
            if child.tag == 'nd':
                node_ref = str(child.attrib['ref'])
                node_refs.append(node_ref)
        return node_refs
