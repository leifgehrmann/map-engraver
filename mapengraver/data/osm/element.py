from typing import Dict


class Element:
    """An OSM node"""
    id: str
    tags: Dict[str, str]

    def __init__(self, osm_element):
        self.id = osm_element.attrib['id']
        self.tags = {}
