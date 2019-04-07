from map.features.generic import PolygonDrawer
from map.layer import OsmLayer, ILayer


class PolygonLayer(OsmLayer):

    fill_color = None
    stroke_color = None
    stroke_width = None

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'PolygonLayer':
        layer = PolygonLayer() \
            .set_parent(parent) \
            .set_osm_map_filter_from_dict(data)
        if 'fill color' in data:
            layer.fill_color = data['fill color']
        if 'stroke color' in data:
            layer.stroke_color = data['stroke color']
        if 'stroke width' in data:
            layer.stroke_width = data['stroke width']
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

        context = map.get_context()
        drawer = PolygonDrawer()
        if self.fill_color is not None:
            drawer.set_fill_color(*self.fill_color)
        if self.stroke_color is not None:
            drawer.set_stroke_color(*self.stroke_color)
        if self.stroke_width is not None:
            drawer.set_stroke_width(self.stroke_width)
        drawer.draw(context, polygons)
