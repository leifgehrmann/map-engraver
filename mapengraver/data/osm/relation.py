from typing import Dict, List
import xml.etree.ElementTree as ElementTree
from . import Member


class Relation:
    """An OSM Relation"""
    id: str
    tags: Dict[str, str]
    members: List[type(Member)]

    def __init__(self, osm_element):
        self.id = osm_element.attrib['id']
        self.members = Relation.get_relation_members(osm_element)
        self.nodes = []
        self.relations = []
        self.neighboring_ways = []
        self.neighboring_relations = []

    @staticmethod
    def get_relation_members(osm_element: ElementTree) -> List[type(Member)]:
        """Get all members for a relation"""
        members = list()
        for child in osm_element:
            if child.tag == 'member':
                members.append(Member(child))
        return members
