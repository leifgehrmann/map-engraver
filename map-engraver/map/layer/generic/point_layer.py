from map.features.generic import PointDrawer
from map.layer import OsmLayer, ILayer


class PointLayer(OsmLayer):

    symbol = None
    size = 1
    circle_fill_color = None
    circle_stroke_color = None
    circle_stroke_width = None

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'PointLayer':
        layer = PointLayer() \
            .set_parent(parent) \
            .set_osm_map_filter_from_dict(data)
        if 'size' in data:
            layer.size = data['size']
        if 'circle fill color' in data:
            layer.circle_fill_color = data['circle fill color']
        if 'circle stroke color' in data:
            layer.circle_stroke_color = data['circle stroke color']
        if 'circle stroke width' in data:
            layer.circle_stroke_width = data['circle stroke width']
        return layer

    def draw(self):
        map = self.parent.get_map()
        map_data = map.get_map_data()
        filtered_map_data = self.osm_map_filter(map_data)
        pipeline = map.get_osm_shapely_conversion_pipeline()

        nodes = filtered_map_data['nodes'].values()

        points = []
        points.extend(pipeline.nodes_to_points(nodes))

        context = map.get_context()
        drawer = PointDrawer()
        if self.size is not None:
            drawer.set_size(self.size)
        if self.circle_fill_color is not None:
            drawer.set_circle_fill_color(*self.circle_fill_color)
        if self.circle_stroke_color is not None:
            drawer.set_circle_stroke_color(*self.circle_stroke_color)
        if self.circle_stroke_width is not None:
            drawer.set_circle_stroke_width(self.circle_stroke_width)
        drawer.draw(context, points)
