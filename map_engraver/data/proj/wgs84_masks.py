from shapely.geometry import Polygon


def wgs84_mask() -> Polygon:
    return Polygon([
        (-180, -90),
        (-180, 90),
        (180, 90),
        (180, -90),
        (-180, -90)
    ])
