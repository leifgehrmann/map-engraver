from shapely.geometry import Polygon


def wgs84_mask() -> Polygon:
    return Polygon([
        (-90, -180),
        (-90, 180),
        (90, 180),
        (90, -180),
        (-90, -180)
    ])
