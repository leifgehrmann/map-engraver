from typing import Tuple, Callable, Optional, Union

from map import MapConfig
import pyproj
import cairocffi as cairo

import osmparser
from map.imap import IMap
from map.layer import Layer
import os

from osmshapely.ops import ConverterPipeline, ShapelyTransformer, ShapelyClipper


class Map(IMap):

    map_config = None
    map_data = None
    projection_function = None
    logging_function = None
    progress_function = None
    serializer = None
    surface = None
    context = None

    def __init__(self, map_config: MapConfig):
        self.map_config = map_config
        self.serializer = map_config.get_cache_serializer()
        self.projection_function = self._generate_projection_function()

    def prepare_map_data(self) -> 'Map':
        osm_map = osmparser.Map()
        # Todo: Add progress functions here
        for osm_map_data_file in self.map_config.get_osm_map_data_files():
            osm_map.add_osm_file(osm_map_data_file)
        self.map_data = osm_map
        return self

    def set_logging_function(self, logging_function) -> 'Map':
        self.logging_function = logging_function
        return self

    def set_progress_function(self, progress_function) -> 'Map':
        self.progress_function = progress_function
        return self

    def get_surface(self) -> cairo.Surface:
        return self.surface

    def get_context(self) -> cairo.Context:
        return self.context

    def get_map_config(self) -> MapConfig:
        return self.map_config

    def get_map_data(self) -> osmparser.Map:
        return self.map_data

    def get_map_projection_function(self) -> Callable[
        [float, float, Optional[float]],
        Union[Tuple[float, float], Tuple[float, float, float]]
    ]:
        return self.projection_function

    def _generate_projection_function(self) -> Callable[
        [float, float, Optional[float]],
        Union[Tuple[float, float], Tuple[float, float, float]]
    ]:

        wgs84_projection = pyproj.Proj(init='epsg:4326')
        mc_projection = self.map_config.get_map_projection()
        mc_origin = self.map_config.get_map_projection_origin()
        mc_scale = self.map_config.get_map_projection_units_per_canvas_unit()

        def project_to_canvas(
                lon: float,
                lat: float,
                alt: Optional[float] = None
        ) -> Union[Tuple[float, float], Tuple[float, float, float]]:
            x, y = pyproj.transform(wgs84_projection, mc_projection, lon, lat)
            x -= mc_origin[0]
            y -= mc_origin[1]
            x /= mc_scale
            y /= mc_scale
            y *= -1  # positive y values in PDFs go downwards

            if alt is None:
                return x, y
            else:
                return x, y, alt

        return project_to_canvas

    def _get_output_directory(self):
        return self.map_config.get_output_directory()

    def _get_output_filename(self):
        output_name = self.map_config.get_name()
        canvas_format = self.map_config.get_canvas_format()
        return "%s.%s" % (output_name, canvas_format)

    def _get_output_filepath(self):
        return "%s%s" % (
            self._get_output_directory(),
            self._get_output_filename()
        )

    def _create_map_surface(self) -> Tuple[cairo.Surface, cairo.Context]:
        pixels_per_point = 0.75
        points_per_inch = 72
        mm_per_inch = 25.4

        canvas_dimensions = self.map_config.get_canvas_unit_dimensions()
        canvas_width, canvas_height = canvas_dimensions
        canvas_format = self.map_config.get_canvas_format()
        canvas_scale = 1

        if canvas_format in ['pdf', 'ps']:
            canvas_width *= points_per_inch
            canvas_height *= points_per_inch
            canvas_scale *= points_per_inch

            if self.map_config.get_canvas_units() == 'pt':
                canvas_width /= points_per_inch
                canvas_height /= points_per_inch
                canvas_scale /= points_per_inch
            elif self.map_config.get_canvas_units() == 'mm':
                canvas_width /= mm_per_inch
                canvas_height /= mm_per_inch
                canvas_scale /= mm_per_inch
        else:
            canvas_width *= self.map_config.get_canvas_pixels_per_unit()
            canvas_height *= self.map_config.get_canvas_pixels_per_unit()
            canvas_scale *= self.map_config.get_canvas_pixels_per_unit()

            canvas_width *= pixels_per_point
            canvas_height *= pixels_per_point
            canvas_scale *= pixels_per_point

        output_directory = self.map_config.get_output_directory()
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        output_filepath = self._get_output_filepath()

        if canvas_format == 'pdf':
            surface = cairo.PDFSurface(
                output_filepath,
                canvas_width,
                canvas_height
            )
        elif canvas_format == 'svg':
            surface = cairo.SVGSurface(
                output_filepath,
                canvas_width,
                canvas_height
            )
        elif canvas_format == 'png':
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(canvas_width),
                int(canvas_height)
            )
        else:
            raise Exception('Unexpected Format: %s' % canvas_format)

        context = cairo.Context(surface)

        context.scale(canvas_scale, canvas_scale)  # Normalizing the canvas
        return surface, context

    def get_osm_shapely_conversion_pipeline(self) -> ConverterPipeline:
        pipeline = ConverterPipeline(self.get_map_data())

        pipeline.set_transformer(
            ShapelyTransformer(func=self.get_map_projection_function())
        )

        clip_boundaries = self.map_config.get_map_data_clip_boundaries()
        if clip_boundaries is not None:
            clipper = ShapelyClipper(clip_boundaries)
            pipeline.set_clipper(clipper)

        return pipeline

    def draw(self):
        self.surface, self.context = self._create_map_surface()
        Layer.create_from_yaml(self.map_config.get_main_layer_file(), self).draw_layers()
        self.surface.flush()

        # Special edge case for ImageSurfaces
        if isinstance(self.surface, cairo.ImageSurface):
            self.surface.write_to_png(self._get_output_filepath())

        self.surface.finish()
