from typing import Dict


class Node:
    """An OSM node"""
    id: str
    lat: float
    lon: float
    tags: Dict[str, str]

    def __init__(self, osm_element):
        self.id = osm_element.attrib['id']
        self.lat = float(osm_element.attrib['lat'])
        self.lon = float(osm_element.attrib['lon'])
        self.tags = {}
        self.member_of_ways = []
        self.member_of_relations = []