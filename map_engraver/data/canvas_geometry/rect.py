from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit


def rect(bbox: CanvasBbox) -> Polygon:
    if bbox.width.pt <= 0:
        raise Exception('width of bbox cannot be 0 or less.')
    if bbox.height.pt <= 0:
        raise Exception('height of bbox cannot be 0 or less.')
    return Polygon([
        bbox.min_pos.pt,
        CanvasCoordinate(bbox.max_pos.x, bbox.min_pos.y).pt,
        bbox.max_pos.pt,
        CanvasCoordinate(bbox.min_pos.x, bbox.max_pos.y).pt
    ])


def rounded_rect(
        bbox: CanvasBbox,
        radius=CanvasUnit(0)
) -> Polygon:
    if bbox.width.pt <= 0:
        raise Exception('width of bbox cannot be 0 or less.')
    if bbox.height.pt <= 0:
        raise Exception('height of bbox cannot be 0 or less.')
    if radius.pt < 0:
        raise Exception('radius cannot be 0 or less.')

    ul = bbox.min_pos
    ur = CanvasCoordinate(bbox.max_pos.x, bbox.min_pos.y)
    br = bbox.max_pos
    bl = CanvasCoordinate(bbox.min_pos.x, bbox.max_pos.y)

    max_radius_pt = min(radius.pt, bbox.width.pt / 2, bbox.height.pt / 2)

    rounded_rect_poly = Polygon([
        # Upper left
        (ul.x.pt, ul.y.pt + max_radius_pt),
        (ul.x.pt + max_radius_pt, ul.y.pt + max_radius_pt),
        (ul.x.pt + max_radius_pt, ul.y.pt),
        # Upper right
        (ur.x.pt - max_radius_pt, ur.y.pt),
        (ur.x.pt - max_radius_pt, ur.y.pt + max_radius_pt),
        (ur.x.pt, ur.y.pt + max_radius_pt),
        # Bottom right
        (br.x.pt, br.y.pt - max_radius_pt),
        (br.x.pt - max_radius_pt, br.y.pt - max_radius_pt),
        (br.x.pt - max_radius_pt, br.y.pt),
        # Bottom left
        (bl.x.pt + max_radius_pt, bl.y.pt),
        (bl.x.pt + max_radius_pt, bl.y.pt - max_radius_pt),
        (bl.x.pt, bl.y.pt - max_radius_pt),
    ])

    circle_ul = Point((ul.x.pt + max_radius_pt, ul.y.pt + max_radius_pt))
    circle_ul = circle_ul.buffer(max_radius_pt)
    circle_ur = Point((ur.x.pt - max_radius_pt, ur.y.pt + max_radius_pt))
    circle_ur = circle_ur.buffer(max_radius_pt)
    circle_bl = Point((bl.x.pt + max_radius_pt, bl.y.pt - max_radius_pt))
    circle_bl = circle_bl.buffer(max_radius_pt)
    circle_br = Point((br.x.pt - max_radius_pt, br.y.pt - max_radius_pt))
    circle_br = circle_br.buffer(max_radius_pt)

    x = unary_union(
        [rounded_rect_poly, circle_ul, circle_ur, circle_bl, circle_br]
    )
    return x
