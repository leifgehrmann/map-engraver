import unittest
from pathlib import Path

from map_engraver.data.osm import Parser, Node
from map_engraver.data.osm.filter import filter_elements
from map_engraver.data.osm_shapely.natural_coastline import \
    natural_coastline_to_multi_polygon, CoastlineOutputType


class TestNaturalCoastline(unittest.TestCase):
    def test_natural_coastline_conversion(self):
        path = Path(__file__).parent.joinpath('coastline_data.osm')

        osm_map = Parser.parse(path)

        bbox_nodes = list(filter_elements(
            osm_map,
            lambda _, node: (
                    'bbox' in node.tags
            ),
            filter_ways=False,
            filter_relations=False
        ).nodes.values())

        assert len(bbox_nodes) == 2
        min_node = bbox_nodes[0]
        max_node = bbox_nodes[1]
        if bbox_nodes[1].tags['bbox'] == 'min':
            min_node = bbox_nodes[1]
            max_node = bbox_nodes[0]

        bounds = (min_node.lat, min_node.lon, max_node.lat, max_node.lon)
        print(bounds)

        natural_coastline_to_multi_polygon(osm_map, bounds, CoastlineOutputType.LAND)
