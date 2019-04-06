from graphicshelper import ShapelyHelper
from map.features.nature import WaterDrawer
from map.layer import OsmLayer, ILayer


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
        filtered_map_data = self.osm_map_filter(map_data)
        pipeline = map.get_osm_shapely_conversion_pipeline()

        ways = filtered_map_data['ways'].values()
        relations = filtered_map_data['relations'].values()

        polygons = []
        polygons.extend(pipeline.ways_to_polygons(ways))
        polygons.extend(pipeline.relations_to_polygons(relations))

        polygons = ShapelyHelper.unionize_polygon_array(polygons)

        context = map.get_context()
        drawer = WaterDrawer()
        drawer.draw(context, polygons)
