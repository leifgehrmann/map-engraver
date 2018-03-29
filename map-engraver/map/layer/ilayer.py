from typing import Union, List

from map.imap import IMap


class ILayer:

    @staticmethod
    def create_from_yaml(file_path: str, parent: Union[IMap, 'ILayer']):
        pass

    def get_map(self) -> IMap:
        pass

    def get_parent(self) -> Union[IMap, 'ILayer']:
        pass

    def get_name(self) -> str:
        pass

    def get_layers(self) -> List[dict]:
        pass

    def get_relative_directory(self) -> str:
        pass

    def set_config(self, config: dict) -> 'ILayer':
        pass

    def set_relative_directory(self, relative_directory: str) -> 'ILayer':
        pass

    def set_parent(self, parent: Union[IMap, 'ILayer']) -> 'ILayer':
        pass

    def draw_layers(self):
        pass

    def _draw_layer(self, layer):
        pass