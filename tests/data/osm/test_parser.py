from pathlib import Path

import unittest

from mapengraver.data.osm import Parser


class TestParser(unittest.TestCase):
    def test_parser_reads_all_objects(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)

        assert len(osm_map.nodes) > 0
        assert len(osm_map.ways) == 6
        assert len(osm_map.relations) == 2

        assert osm_map.get_node('-101762').tags['amenity'] == 'bank'
        assert osm_map.get_way('-101931').tags['highway'] == 'service'
        assert osm_map.get_relation('-99750').tags['building'] == 'yes'

        assert osm_map.get_nodes_for_way('-101873')[1].tags['name'] == 'Beta'
