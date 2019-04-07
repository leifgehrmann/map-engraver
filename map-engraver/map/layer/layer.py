import yaml

import os
from typing import List, Union

from map.layer.buildings import WallLayer
from map.layer.buildings import BuildingLayer
from map.layer.generic import LabelPathLayer
from map.layer.nature import GrassLayer
from map.layer.highway import RailwayLayer
from map.layer.nature import WaterLayer
from map.layer.svg_layer import SvgLayer
from map.layer.ilayer import ILayer
from ..layer.background_layer import BackgroundLayer
from ..layer.margin_layer import MarginLayer
from ..map import IMap


class Layer(ILayer):

    config = {}
    relative_directory = '/'
    parent = None

    @staticmethod
    def create_from_yaml(file_path: str, parent: Union[IMap, 'Layer']):
        file = open(file_path, 'r')
        config = yaml.safe_load(file)
        directory = os.path.dirname(file_path)
        return Layer().set_config(config)\
            .set_relative_directory(directory)\
            .set_parent(parent)

    def get_map(self) -> IMap:
        parent = self.get_parent()
        if isinstance(parent, Layer):
            return parent.get_map()
        elif isinstance(parent, IMap):
            return parent

    def get_parent(self) -> Union[IMap, 'Layer']:
        return self.parent

    def get_name(self) -> str:
        if 'name' in self.config:
            return self.config['name']

    def get_layers(self) -> List[dict]:
        if 'layers' in self.config:
            return self.config['layers']
        return []

    def get_relative_directory(self) -> str:
        return self.relative_directory

    def set_config(self, config: dict) -> 'Layer':
        self.config = config
        return self

    def set_relative_directory(self, relative_directory: str) -> 'Layer':
        self.relative_directory = os.path.realpath(relative_directory)
        return self

    def set_parent(self, parent: Union[IMap, 'Layer']) -> 'Layer':
        self.parent = parent
        return self

    def draw_layers(self):
        print("Drawing Layer: %s (%s)" % (self.get_name(), self.get_relative_directory()))
        for layer in self.get_layers():
            self._draw_layer(layer)

    def _draw_layer(self, layer: dict):
        try:
            layer_type = layer['type']
            print(layer_type)
        except KeyError:
            print("Invalid layer")
            return

        if layer_type == 'SubLayer':
            file_path = os.path.join(self.relative_directory, layer['file'])
            Layer.create_from_yaml(file_path, self).draw_layers()
        elif layer_type == 'Background':
            BackgroundLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Margin':
            MarginLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Svg':
            SvgLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Walls':
            WallLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Railways':
            RailwayLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'LabelPaths':
            LabelPathLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Grass':
            GrassLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Water':
            WaterLayer.create_from_dict(layer, self).draw()
        elif layer_type == 'Buildings':
            BuildingLayer.create_from_dict(layer, self).draw()
