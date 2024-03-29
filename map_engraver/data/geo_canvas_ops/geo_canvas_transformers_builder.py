import math

from typing import Optional

import pyproj

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo.geo_coordinate_transformers import \
    transform_geo_coordinates_to_new_crs
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers import \
    build_crs_to_canvas_transformer, \
    build_canvas_to_crs_transformer


class GeoCanvasTransformersBuilder:
    crs: Optional[pyproj.CRS]
    rotation: float
    scale: Optional[GeoCanvasScale]
    origin_for_geo: Optional[GeoCoordinate]
    origin_for_canvas: Optional[CanvasCoordinate]
    data_crs: Optional[pyproj.CRS]
    is_crs_yx: bool
    is_data_yx: bool

    def __init__(self):
        self.crs = None
        self.rotation = 0
        self.scale = None
        self.origin_for_geo = None
        self.origin_for_canvas = None
        self.data_crs = None
        self.is_crs_yx = False
        self.is_data_yx = False

    def set_crs(self, crs: Optional[pyproj.CRS]):
        self.crs = crs

    def set_rotation(self, rotation: float):
        self.rotation = rotation

    def set_scale(self, scale: Optional[GeoCanvasScale]):
        self.scale = scale

    def set_origin_for_geo(self, origin_for_geo: Optional[GeoCoordinate]):
        self.origin_for_geo = origin_for_geo

    def set_origin_for_canvas(
            self, origin_for_canvas: Optional[CanvasCoordinate]
    ):
        self.origin_for_canvas = origin_for_canvas

    def set_data_crs(self, data_crs: Optional[pyproj.CRS]):
        self.data_crs = data_crs

    def set_is_crs_yx(self, is_crs_yx: bool):
        self.is_crs_yx = is_crs_yx

    def set_is_data_yx(self, is_data_yx: bool):
        self.is_data_yx = is_data_yx

    def set_scale_and_origin_from_coordinates_and_crs(
            self,
            crs: pyproj.CRS,
            geo_a: GeoCoordinate,
            geo_b: GeoCoordinate,
            canvas_a: CanvasCoordinate,
            canvas_b: CanvasCoordinate,
    ):
        # Transform geo_a and geo_b to match the crs
        new_geo_a: GeoCoordinate
        new_geo_b: GeoCoordinate
        new_geo_a, new_geo_b = transform_geo_coordinates_to_new_crs(
            [geo_a, geo_b], crs
        )

        if new_geo_a.x == float('inf') or new_geo_b.x == float('inf'):
            raise Exception(
                'geo_a and geo_b must be projectable using crs'
            )

        self.crs = crs
        self.origin_for_geo = GeoCoordinate(
            (new_geo_a.x + new_geo_b.x) / 2,
            (new_geo_a.y + new_geo_b.y) / 2,
            crs
        )

        self.origin_for_canvas = CanvasCoordinate.from_pt(
            (canvas_a.x.pt + canvas_b.x.pt) / 2,
            (canvas_a.y.pt + canvas_b.y.pt) / 2,
        )

        geo_distance = math.sqrt(
            math.pow(new_geo_b.x - new_geo_a.x, 2) +
            math.pow(new_geo_b.y - new_geo_a.y, 2)
        )

        canvas_distance = math.sqrt(
            math.pow(canvas_b.x.pt - canvas_a.x.pt, 2) +
            math.pow(canvas_b.y.pt - canvas_a.y.pt, 2)
        )

        self.scale = GeoCanvasScale(
            geo_distance,
            CanvasUnit.from_pt(canvas_distance)
        )

    def copy(self) -> 'GeoCanvasTransformersBuilder':
        builder = GeoCanvasTransformersBuilder()
        builder.set_crs(self.crs)
        builder.set_origin_for_geo(self.origin_for_geo)
        builder.set_origin_for_canvas(self.origin_for_canvas)
        builder.set_scale(self.scale)
        builder.set_data_crs(self.data_crs)
        builder.set_is_crs_yx(self.is_crs_yx)
        builder.set_is_data_yx(self.is_data_yx)
        builder.set_rotation(self.rotation)
        return builder

    def build_crs_to_canvas_transformer(self):
        if (
                self.crs is None or
                self.scale is None or
                self.origin_for_geo is None or
                self.origin_for_canvas is None
        ):
            raise Exception(
                'crs, scale, and origins must be defined'
            )
        return build_crs_to_canvas_transformer(
            self.crs,
            self.scale,
            self.origin_for_geo,
            self.origin_for_canvas,
            self.data_crs,
            rotation=self.rotation,
            is_crs_yx=self.is_crs_yx,
            is_data_yx=self.is_data_yx
        )

    def build_canvas_to_crs_transformer(self):
        if (
                self.crs is None or
                self.scale is None or
                self.origin_for_geo is None or
                self.origin_for_canvas is None
        ):
            raise Exception(
                'crs, scale, and origins must be defined'
            )
        return build_canvas_to_crs_transformer(
            self.crs,
            self.scale,
            self.origin_for_geo,
            self.origin_for_canvas,
            self.data_crs,
            rotation=self.rotation,
            is_crs_yx=self.is_crs_yx,
            is_data_yx=self.is_data_yx
        )
