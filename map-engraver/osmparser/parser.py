from typing import Dict
import xml.etree.ElementTree as ElementTree

import osmparser


class Parser:
    @staticmethod
    def get_element_tags(osm_element: ElementTree) -> Dict[str, str]:
        """Get all key value information for an element (node, way, or relation)"""
        key_values = dict()
        for child in osm_element:
            if child.tag == 'tag':
                key = child.attrib['k']
                value = child.attrib['v']
                key_values[key] = value
        return key_values

    @staticmethod
    def get_nodes(osm_root: ElementTree) -> object:
        """Get all the nodes from the osm file indexed by node id"""
        nodes = dict()
        for osm_element in osm_root:
            element_type = osm_element.tag
            if element_type == 'node':
                nodes[osm_element.attrib['id']] = osmparser.Node(osm_element)
        return nodes

    @staticmethod
    def get_ways(osm_root: ElementTree) -> Dict[str, type(osmparser.Way)]:
        """Get all the ways from the osm file indexed by way id"""
        ways = dict()
        for osm_element in osm_root:
            element_type = osm_element.tag
            if element_type == 'way':
                ways[osm_element.attrib['id']] = osmparser.Way(osm_element)
        return ways

    @staticmethod
    def get_relations(osm_root: ElementTree) -> Dict[str, type(osmparser.Relation)]:
        """Get all the relations from the osm file indexed by relation id"""
        relations = dict()
        for osm_element in osm_root:
            element_type = osm_element.tag
            if element_type == 'relation':
                relations[osm_element.attrib['id']] = osmparser.Relation(osm_element)
        return relations
