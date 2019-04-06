from typing import Tuple, Callable, Optional, Union

from map import MapConfig
import pyproj
import cairocffi as cairo

import osmparser
from map.imap import IMap
from map.layer import Layer
import os

from osmshapely.ops import ConverterPipeline, ShapelyTransformer


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
        mc_extents = self.map_config.get_map_projection_extents()
        mc_origin = self.map_config.get_map_projection_origin()
        mc_scale = self.map_config.get_map_scale()

        if mc_extents is not None:
            extent_min_lon, extent_min_lat = pyproj.transform(
                mc_projection,
                wgs84_projection,
                mc_extents[0],
                mc_extents[1]
            )

            extent_max_lon, extent_max_lat = pyproj.transform(
                mc_projection,
                wgs84_projection,
                mc_extents[2],
                mc_extents[3]
            )
        else:
            extent_min_lon, extent_min_lat, extent_max_lon, extent_max_lat = (
                None, None, None, None
            )

        def project_to_canvas(
                lon: float,
                lat: float,
                alt: Optional[float] = None
        ) -> Union[Tuple[float, float], Tuple[float, float, float]]:
            if extent_max_lon is not None and lon >= extent_max_lon:
                lon = extent_max_lon
            if extent_min_lon is not None and lon <= extent_min_lon:
                lon = extent_min_lon
            if extent_max_lat is not None and lat >= extent_max_lat:
                lat = extent_max_lat
            if extent_min_lat is not None and lat <= extent_min_lat:
                lat = extent_min_lat
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

    def _create_map_surface(self) -> Tuple[cairo.Surface, cairo.Context]:
        pdf_inch = 72

        canvas_width, canvas_height = self.map_config.get_dimensions()
        pdf_width = canvas_width * pdf_inch
        pdf_height = canvas_height * pdf_inch
        pdf_scale = pdf_inch

        if self.map_config.get_units() == 'mm':
            mm_in_an_inch = 25.4
            pdf_width /= mm_in_an_inch
            pdf_height /= mm_in_an_inch
            pdf_scale /= mm_in_an_inch

        output_dir = self.map_config.get_output_directory()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = output_dir + self.map_config.get_name() + ".pdf"

        surface = cairo.PDFSurface(output_file, pdf_width, pdf_height)
        context = cairo.Context(surface)

        context.scale(pdf_scale, pdf_scale)  # Normalizing the canvas
        return surface, context

    def get_osm_shapely_conversion_pipeline(self) -> ConverterPipeline:
        pipeline = ConverterPipeline(self.get_map_data())
        pipeline.set_transformer(
            ShapelyTransformer(func=self.get_map_projection_function())
        )
        return pipeline

    def draw(self):
        self.surface, self.context = self._create_map_surface()
        Layer.create_from_yaml(self.map_config.get_main_layer_file(), self).draw_layers()
        self.surface.flush()
        self.surface.finish()
