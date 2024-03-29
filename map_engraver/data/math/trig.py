from math import acos, pi, sqrt

from typing import Tuple, Optional

Coord = Tuple[float, float]
Vector = Tuple[float, float]
UnitVector = Vector
Matrix2D = Tuple[Vector, Vector]

# A line is defined by two vectors, its origin, and its direction
Line = Tuple[Coord, UnitVector]


def _diff(a: Coord, b: Coord) -> Coord:
    return (
        (b[0] - a[0]),
        (b[1] - a[1])
    )


def _magnitude(v: Vector) -> float:
    return sqrt(v[0] * v[0] + v[1] * v[1])


def _dot(a: Vector, b: Vector) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _det(m: Matrix2D) -> float:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def obtuse_angle(a: Coord, b: Coord, c: Coord) -> float:
    """
    Given all three coordinates of a triangle, this function returns the
    angle between `ca` and `cb` in degrees.
    """
    ca = _diff(c, a)
    cb = _diff(c, b)
    ca_dot_bc = _dot(ca, cb)
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


def line_intersection(l1: Line, l2: Line) -> Optional[Coord]:
    # https://math.stackexchange.com/a/406895
    a = _det((
        (l1[1][0], -l2[1][0]),
        (l1[1][1], -l2[1][1])
    ))
    if a == 0:
        return None
    a1 = _det((
        (l2[0][0] - l1[0][0], -l2[1][0]),
        (l2[0][1] - l1[0][1], -l2[1][1])
    ))
    return (
        l1[0][0] + (a1 / a) * l1[1][0],
        l1[0][1] + (a1 / a) * l1[1][1]
    )


def scalar_between_lines_origin_and_projected_point(
    line: Line,
    point: Coord
) -> float:
    """
    Returns the scalar which represents the distance and direction between the
    line's origin, and a point's projected position on the line. It's similar
    to the "distance between a point and a line" problem, but instead it's the
    point on the line and the line's origin.

    Essentially the formula is: (a - p) · n

    Wikimedia has a useful graphic that illustrates this.
    https://commons.wikimedia.org/wiki/File:Distance_from_a_point_to_a_line.svg

    :param line:
    :param angle:
    :param point:
    :return:
    """
    return _dot(_diff(line[0], point), line[1])
