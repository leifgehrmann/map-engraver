from map.layer import ILayer


class CacheableLayer:

    serializer = None
    cache_name = None

    def get_cache_name(self) -> str:
        return self.cache_name

    def set_cache_name_from_dict(self, data: dict, parent: ILayer) -> 'CacheableLayer':
        if 'cache' in data:
            self.cache_name = data['cache']['name']
            self.serializer = parent.get_map().get_map_config().get_cache_serializer()
        return self

    def cache_has_result(self) -> bool:
        return self.serializer.is_serialized(self.get_cache_name())

    def cache_generate_result(self):
        raise NotImplementedError

    def cache_store_result(self, result):
        self.serializer.serialize(self.get_cache_name(), result)

    def cache_load_result(self):
        return self.serializer.unserialize(self.get_cache_name())
