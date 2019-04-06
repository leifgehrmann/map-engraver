from map.features.buildings import WallDrawer
from map.layer import ILayer, OsmLayer


class WallLayer(OsmLayer):

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'WallLayer':
        layer = WallLayer()\
            .set_parent(parent)\
            .set_osm_map_filter_from_dict(data)
        return layer

    def draw(self):
        map = self.parent.get_map()
        map_data = map.get_map_data()
        filtered_map_data = self.osm_map_filter(map_data)
        pipeline = map.get_osm_shapely_conversion_pipeline()

        ways = filtered_map_data['ways'].values()

        line_strings = []
        line_strings.extend(pipeline.ways_to_line_strings(ways))

        context = map.get_context()
        drawer = WallDrawer()
        drawer.draw_walls(context, line_strings)
