from map.layer import ILayer


class Sublayer:

    parent = None

    def set_parent(self, parent: ILayer) -> 'Sublayer':
        self.parent = parent
        return self
