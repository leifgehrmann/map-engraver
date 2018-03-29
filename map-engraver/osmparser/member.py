from enum import Enum, auto


class MemberTypes(Enum):
    WAY = auto()
    NODE = auto()


class Member:
    type: MemberTypes
    ref: str
    role: str
    """An OSM node"""

    def __init__(self, osm_element):
        if osm_element.attrib['type'] == 'way':
            self.type = MemberTypes.WAY
        else:
            self.type = MemberTypes.NODE
        self.ref = osm_element.attrib['ref']
        self.role = osm_element.attrib['role']
