from math import acos, pi, sqrt

from typing import Tuple

Coord = Tuple[float, float]
Vector = Tuple[float, float]


def _diff(a: Coord, b: Coord) -> Coord:
    return (
        (b[0] - a[0]),
        (b[1] - a[1])
    )


def _magnitude(v: Vector) -> float:
    return sqrt(v[0] * v[0] + v[1] * v[1])


def obtuse_angle(a: Coord, b: Coord, c: Coord):
    """
    Given all three coordinates of a triangle, this function returns the
    angle between `ca` and `cb` in degrees.

    :param a:
    :param b:
    :param c:
    :return:
    """
    ca = _diff(c, a)
    cb = _diff(c, b)
    ca_dot_bc = ca[0] * cb[0] + ca[1] * cb[1]
    mag_mul = _magnitude(ca) * _magnitude(cb)
    if mag_mul == 0:
        return float('inf')
    adj_hyp = ca_dot_bc / mag_mul
    # Sigh... we need to handle floating point errors.
    if adj_hyp < -1:
        return 180
    if adj_hyp > 1:
        return 0
    angle_radians = acos(adj_hyp)
    return angle_radians / pi * 180
