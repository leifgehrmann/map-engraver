import os

import importlib.util
from typing import Callable

from map.layer import Sublayer
from osmparser.map import Map as OsmMap


class OsmLayer(Sublayer):
    osm_map_filter = None

    @staticmethod
    def load_function_from_file(file: str, function_name: str) -> Callable:
        spec = importlib.util.spec_from_file_location(function_name, file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, function_name)

    def set_osm_map_filter(self, osm_map_filter: Callable[[OsmMap], dict]):
        self.osm_map_filter = osm_map_filter

    def set_osm_map_filter_from_dict(self, data: dict) -> 'OsmLayer':
        if 'filter' in data:
            file = os.path.join(self.parent.get_relative_directory(), data['filter']['file'])
            filter_function_name = data['filter']['func']
            filter_function = OsmLayer.load_function_from_file(file, filter_function_name)
            self.set_osm_map_filter(filter_function)
        return self
