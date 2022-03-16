import math
from operator import itemgetter

from pyproj import CRS, Transformer
from shapely.geometry import Polygon


def orthographic_mask(crs: CRS, resolution=16, threshold=1) -> Polygon:
    """

    :param crs:
    :param resolution: Determines the number of segments used to approximate a
                       quarter circle around a point.
    :param threshold: The mask's edge precision, measured in units of the CRS.
    :return:
    """
    transformer = Transformer.from_proj(
        crs,
        CRS.from_epsg(4326)
    )
    points = []
    for i in range(30):
        angle = i * math.pi * 2 / resolution * 4
        radius = _binary_search_edge(crs, angle, threshold)
        position = transformer.transform(
            math.cos(angle) * radius,
            math.sin(angle) * radius
        )
        points.append(position)

    # Extend the sorted points with
    origin = transformer.transform(0, 0)
    if origin[1] != 0:
        # Sort points by longitude
        points = sorted(points, key=itemgetter(0))

        def sign(x: float) -> float:
            return math.copysign(1, x)

        # Extend the path by including points at the North or South Pole.
        points.extend([
            (180, points[-1][1]),
            (180, sign(origin[1]) * 90),
            (-180, sign(origin[0]) * 90),
            (-180, points[0][1])
        ])

    return Polygon(points)


def _binary_search_edge(crs: CRS, angle: float, threshold=1) -> float:
    transformer = Transformer.from_proj(
        crs,
        CRS.from_epsg(4326)
    )
    min_r = min(crs.ellipsoid.semi_minor_metre, crs.ellipsoid.semi_major_metre)
    max_r = max(crs.ellipsoid.semi_minor_metre, crs.ellipsoid.semi_major_metre)
    pivot_r = 0
    while max_r - min_r > threshold:
        pivot_r = (min_r + max_r) / 2
        x = math.cos(angle) * pivot_r
        y = math.sin(angle) * pivot_r
        if (transformer.transform(x, y))[0] == float('inf'):
            max_r = pivot_r
        else:
            min_r = pivot_r

    return pivot_r
