from map_engraver.canvas.canvas_unit import CanvasUnit


class GeoCanvasScale:
    """
    An object that represents the number of geo units per canvas units.

    For example, if you want the scale: 1 centimeter for every 100 meters, you
    would use: `GeoCanvasScale(100, CanvasUnit.from_cm(1))` (Assuming that
    the Coordinate Reference System being used is in meters).
    """
    geo_units: float
    canvas_units: CanvasUnit

    def __init__(self, geo_units: float, canvas_units: CanvasUnit):
        self.geo_units = geo_units
        self.canvas_units = canvas_units
