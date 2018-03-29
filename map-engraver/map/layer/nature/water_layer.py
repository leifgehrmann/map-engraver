from shapely.geometry import Polygon

from map.features.nature import WaterDrawer
from map.layer import OsmLayer, ILayer
from osmparser.convert import Convert as OsmConvert, WayToPolygonError


class WaterLayer(OsmLayer):

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'WaterLayer':
        layer = WaterLayer() \
            .set_parent(parent) \
            .set_osm_map_filter_from_dict(data)
        return layer

    def draw(self):
        map = self.parent.get_map()
        map_data = map.get_map_data()
        map_projection = self.parent.get_map().get_map_projection_function()
        filtered_map_data = self.osm_map_filter(map_data)

        polygons = []
        for way in filtered_map_data['ways'].values():
            try:
                polygon = OsmConvert.way_to_polygon(map_data, way, map_projection)
                if isinstance(polygon, Polygon):
                    polygons.append(polygon)
            except WayToPolygonError:
                continue

        context = map.get_context()
        drawer = WaterDrawer()
        drawer.draw(context, polygons)
