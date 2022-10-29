import unittest
from pathlib import Path
from typing import Tuple

from map_engraver.data.osm import Parser, Osm
from map_engraver.data.osm.filter import filter_elements
from map_engraver.data.osm_shapely.natural_coastline import \
    natural_coastline_to_multi_polygon, CoastlineOutputType


class TestNaturalCoastline(unittest.TestCase):
    def parse_osm(
            self,
            filename: str
    ) -> Tuple[Osm, Tuple[float, float, float, float]]:
        path = Path(__file__).parent.joinpath(filename)

        osm_map = Parser.parse(path)

        bbox_nodes = list(filter_elements(
            osm_map,
            lambda _, node: (
                    'bbox' in node.tags
            ),
            filter_ways=False,
            filter_relations=False
        ).nodes.values())

        self.assertEqual(
            len(bbox_nodes),
            2,
            'OSM file did not contain bbox nodes.'
        )
        min_node = bbox_nodes[0]
        max_node = bbox_nodes[1]
        if bbox_nodes[1].tags['bbox'] == 'min':
            min_node = bbox_nodes[1]
            max_node = bbox_nodes[0]

        bounds = (min_node.lat, min_node.lon, max_node.lat, max_node.lon)

        return osm_map, bounds

    def test_incomplete_natural_coastline(self):
        osm_map, bounds = self.parse_osm('coastline_data.osm')

        land = natural_coastline_to_multi_polygon(
            osm_map,
            bounds,
            CoastlineOutputType.LAND
        )

        self.assertEqual(len(land.geoms), 8)

        water = natural_coastline_to_multi_polygon(
            osm_map,
            bounds,
            CoastlineOutputType.WATER
        )

        self.assertEqual(len(water.geoms), 3)

    def test_map_with_only_lake_coastline_returns_land_safely(self):
        osm_map, bounds = self.parse_osm('coastline_lake_in_land_data.osm')

        land = natural_coastline_to_multi_polygon(
            osm_map,
            bounds,
            CoastlineOutputType.LAND
        )
        self.assertEqual(len(land.geoms), 1)
        self.assertEqual(len(land.geoms[0].interiors), 1)

        water = natural_coastline_to_multi_polygon(
            osm_map,
            bounds,
            CoastlineOutputType.WATER
        )
        self.assertEqual(len(water.geoms), 1)
        self.assertEqual(len(water.geoms[0].interiors), 0)

    def test_empty_natural_coastline_raises_exception(self):
        osm_map, bounds = self.parse_osm('coastline_empty_data.osm')

        with self.assertRaisesRegex(
            Exception,
            'One or more OSM ways with the tag natural=coastline are required.'
        ):
            natural_coastline_to_multi_polygon(
                osm_map,
                bounds,
                CoastlineOutputType.LAND
            )

    def test_incomplete_natural_coastline_start_raises_exception(self):
        osm_map, bounds = self.parse_osm('coastline_incomplete_start_data.osm')

        with self.assertRaisesRegex(
            Exception,
            'coastline way starts with a point that is inside the bounds.'
        ):
            natural_coastline_to_multi_polygon(
                osm_map,
                bounds,
                CoastlineOutputType.LAND
            )

    def test_incomplete_natural_coastline_end_raises_exception(self):
        osm_map, bounds = self.parse_osm('coastline_incomplete_end_data.osm')

        with self.assertRaisesRegex(
            Exception,
            'coastline way ends with a point that is inside the bounds.'
        ):
            natural_coastline_to_multi_polygon(
                osm_map,
                bounds,
                CoastlineOutputType.LAND
            )

    def test_nested_natural_coastline_raises_not_implemented_error(self):
        osm_map, bounds = self.parse_osm('coastline_nested_data.osm')

        with self.assertRaises(NotImplementedError):
            natural_coastline_to_multi_polygon(
                osm_map,
                bounds,
                CoastlineOutputType.LAND
            )

    def test_inverse_nested_natural_coastline_raises_not_implemented_error(
        self
    ):
        osm_map, bounds = self.parse_osm('coastline_inverse_nested_data.osm')

        with self.assertRaises(NotImplementedError):
            natural_coastline_to_multi_polygon(
                osm_map,
                bounds,
                CoastlineOutputType.LAND
            )
