from map.features.nature import GrassDrawer
from map.layer import OsmLayer, ILayer


class GrassLayer(OsmLayer):

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'GrassLayer':
        layer = GrassLayer() \
            .set_parent(parent) \
            .set_osm_map_filter_from_dict(data)
        return layer

    def draw(self):
        map = self.parent.get_map()
        map_data = map.get_map_data()
        filtered_map_data = self.osm_map_filter(map_data)
        pipeline = map.get_osm_shapely_conversion_pipeline()

        ways = filtered_map_data['ways'].values()

        polygons = []
        polygons.extend(pipeline.ways_to_polygons(ways))

        context = map.get_context()
        drawer = GrassDrawer()
        drawer.draw(context, polygons)
