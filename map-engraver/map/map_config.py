import yaml
import os
import pyproj
from shapely.geometry import MultiPolygon, Polygon
from typing import List, Tuple, Optional

from serializer import Serializer


class MapConfig:
    relative_directory = '/'
    config = {}

    @staticmethod
    def create_from_yaml(file_path: str) -> 'MapConfig':
        file = open(file_path, 'r')
        config = yaml.safe_load(file)
        map_config = MapConfig(config)
        file_dir = os.path.dirname(file_path)
        map_config.set_relative_directory(file_dir)
        return map_config

    def __init__(self, config: dict):
        self.config = config

    def set_relative_directory(self, relative_directory):
        self.relative_directory = relative_directory

    def get_name(self) -> str:
        return self.config['name']

    def get_dimensions(self) -> tuple:
        return self.config['canvas']['dimensions']

    def get_units(self) -> str:
        try:
            return self.config['canvas']['units']
        except KeyError:
            return 'mm'

    def get_map_scale(self) -> float:
        """Returns the number of meters per unit scale (typically millimeters or inches)"""
        return self.config['projection']['meters per millimeter']

    def get_map_projection_origin(self) -> tuple:
        return self.config['projection']['origin']

    def get_map_projection(self) -> pyproj.Proj:
        return pyproj.Proj(init=self.config['projection']['proj init'])

    def _normalize_path(self, path: str) -> str:
        return os.path.join(self.relative_directory, path)

    def get_main_layer_file(self) -> str:
        return self._normalize_path(self.config['main layer'])

    def get_osm_map_data_files(self) -> List[str]:
        return list(map(self._normalize_path, self.config['map data']))

    def get_map_data_clip_boundaries(
            self
    ) -> Optional[MultiPolygon]:
        if self.config.get('map data clip boundaries') is None:
            return None
        clip_boundaries_data = self.config['map data clip boundaries']
        polygons = []
        for boundary_data in clip_boundaries_data.values():
            coordinates = []
            for coordinates_data in boundary_data:
                coordinates.append(coordinates_data)
            polygons.append(Polygon(coordinates))
        return MultiPolygon(polygons)

    def get_cache_directory(self) -> str:
        return self._normalize_path(self.config['cache directory'])

    def get_cache_serializer(self) -> Serializer:
        return Serializer(self.get_cache_directory())

    def get_output_directory(self):
        return self._normalize_path(self.config['output directory'])
