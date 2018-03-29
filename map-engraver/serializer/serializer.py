import os
import pickle


class Serializer:
    def __init__(self, default_directory):
        self.default_directory = default_directory

    def get_file_path(self, name: str) -> str:
        return os.path.join(self.default_directory, name + '.pkl')

    def is_serialized(self, name):
        return os.path.exists(self.get_file_path(name))

    def serialize(self, name, data):
        self._make_cache_directory()
        file = open(self.get_file_path(name), 'wb')
        pickle.dump(data, file)

    def unserialize(self, name) -> object:
        file = open(self.get_file_path(name), 'rb')
        return pickle.load(file)

    def _make_cache_directory(self):
        if not os.path.exists(self.default_directory):
            os.makedirs(self.default_directory)
