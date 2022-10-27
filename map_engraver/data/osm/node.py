from map_engraver.data.osm import Element


class Node(Element):
    """An OSM node"""
    lat: float
    lon: float

    def __init__(self, osm_element):
        super().__init__(osm_element)
        self.lat = float(osm_element.attrib['lat'])
        self.lon = float(osm_element.attrib['lon'])
