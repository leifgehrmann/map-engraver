from shapely.geometry import LineString

from map.features.highway import RailwayDrawer
from map.layer import ILayer, OsmLayer
from osmparser.convert import Convert as OsmConvert, WayToLineStringError


class RailwayLayer(OsmLayer):

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'RailwayLayer':
        layer = RailwayLayer()\
            .set_parent(parent)\
            .set_osm_map_filter_from_dict(data)
        return layer

    def draw(self):
        map = self.parent.get_map()
        map_data = map.get_map_data()
        map_projection = self.parent.get_map().get_map_projection_function()
        filtered_map_data = self.osm_map_filter(map_data)

        line_strings = []
        for way in filtered_map_data['ways'].values():
            try:
                line_string = OsmConvert.way_to_linestring(map_data, way, map_projection)
                if isinstance(line_string, LineString):
                    line_strings.append(line_string)
            except WayToLineStringError:
                continue

        context = map.get_context()
        drawer = RailwayDrawer()
        drawer.draw_railways(context, line_strings)