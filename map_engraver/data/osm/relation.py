from typing import List
import xml.etree.ElementTree as ElementTree
from . import Member, Element


class Relation(Element):
    """An OSM Relation"""
    members: List[type(Member)]

    def __init__(self, osm_element):
        super().__init__(osm_element)
        self.members = Relation._get_relation_members(osm_element)
        self.nodes = []
        self.relations = []
        self.neighboring_ways = []
        self.neighboring_relations = []

    @staticmethod
    def _get_relation_members(osm_element: ElementTree) -> List[type(Member)]:
        """Get all members for a relation"""
        members = list()
        for child in osm_element:
            if child.tag == 'member':
                members.append(Member(child))
        return members
