from pathlib import Path

import unittest

from mapengraver.data.osm import Parser, Osm, Element, Way
from mapengraver.data.osm.filter import filter_elements


class TestFilter(unittest.TestCase):
    def test_filter_elements(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)

        def my_function(osm: Osm, element: Element) -> bool:
            if isinstance(element, Way):
                return element.tags.get('highway') == 'service'
            return False

        osm_map_subset = filter_elements(osm_map, my_function)

        assert len(osm_map_subset.nodes) == 0
        assert len(osm_map_subset.ways) == 3
        assert len(osm_map_subset.relations) == 0
        assert list(osm_map_subset.ways.keys()) == [
            '-101873',
            '-101889',
            '-101931'
        ]

    def test_filter_elements_with_all_types_excluded(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)

        def my_function(osm: Osm, element: Element) -> bool:
            if isinstance(element, Way):
                return element.tags.get('highway') == 'service'
            return False

        osm_map_subset = filter_elements(
            osm_map,
            my_function,
            filter_nodes=False,
            filter_ways=False,
            filter_relations=False
        )

        assert len(osm_map_subset.nodes) == 0
        assert len(osm_map_subset.relations) == 0
        assert len(osm_map_subset.ways) == 0
