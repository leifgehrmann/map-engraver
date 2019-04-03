import math
from typing import List

from shapely.geometry import Polygon

from graphicshelper import ShapelyHelper
from map.layer import OsmLayer, CacheableLayer, ILayer
from map.features.buildings import Basic as BuildingDrawer
from osmparser.convert import Convert as OsmConvert, WayToPolygonError


class BuildingLayer(OsmLayer, CacheableLayer):
    line_angle = math.pi / 6
    line_separation = 0.3
    high_quality = True
    unionize = True

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'BuildingLayer':
        layer = BuildingLayer() \
            .set_parent(parent) \
            .set_osm_map_filter_from_dict(data) \
            .set_cache_name_from_dict(data, parent)
        if 'line angle' in data:
            layer.line_angle = data['line angle']
        if 'line separation' in data:
            layer.line_separation = data['line separation']
        if 'high quality' in data:
            layer.high_quality = data['high quality']
        if 'union' in data:
            layer.unionize = data['union']
        return layer

    def cache_generate_result(self) -> List[Polygon]:

        map = self.parent.get_map()
        map_data = map.get_map_data()
        filtered_map_data = self.osm_map_filter(map_data)
        map_projection = self.parent.get_map().get_map_projection_function()

        polygons = []
        if 'ways' in filtered_map_data:
            for way in filtered_map_data['ways'].values():
                try:
                    polygon = OsmConvert.way_to_polygon(
                        map_data,
                        way,
                        map_projection
                    )
                    if isinstance(polygon, Polygon):
                        polygons.append(polygon)
                except WayToPolygonError:
                    continue

        if 'relations' in filtered_map_data:
            for way in filtered_map_data['relations'].values():
                try:
                    polygon = OsmConvert.relation_to_polygon(
                        map_data,
                        way,
                        map_projection
                    )
                    if isinstance(polygon, Polygon):
                        polygons.append(polygon)
                except WayToPolygonError:
                    continue

        # Unionization of polygons
        if self.unionize:
            polygons = ShapelyHelper.unionize_polygon_array(polygons)

        return polygons

    def cache_load_result(self) -> List[Polygon]:
        return super(BuildingLayer, self).cache_load_result()

    def draw(self):
        map = self.parent.get_map()
        
        if self.cache_has_result():
            print("Using cached result")
            result = self.cache_load_result()
        else:
            result = self.cache_generate_result()
            if self.cache_is_enabled():
                self.cache_store_result(result)

        context = map.get_context()
        drawer = BuildingDrawer()\
            .set_line_angle(self.line_angle)\
            .set_line_separation(self.line_separation)\
            .set_high_quality(self.high_quality)
        drawer.draw(context, result)
