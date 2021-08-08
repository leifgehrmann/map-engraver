import math

points_per_inch = 72
mm_per_inch = 25.4
points_per_pixel = 0.75
inch_per_mm = 1 / mm_per_inch
mm_per_cm = 10


class CanvasUnit:
    _points: float

    def __init__(self, points: float):
        self._points = points

    @property
    def pt(self) -> float:
        return self._points

    @classmethod
    def from_pt(cls, points: float) -> 'CanvasUnit':
        return CanvasUnit(points)

    @property
    def inches(self) -> float:
        return self._points / points_per_inch

    @classmethod
    def from_in(cls, inches: float) -> 'CanvasUnit':
        return CanvasUnit(inches * points_per_inch)

    @property
    def mm(self) -> float:
        return self._points / inch_per_mm / points_per_inch

    @classmethod
    def from_mm(cls, mm: float) -> 'CanvasUnit':
        return CanvasUnit(mm * inch_per_mm * points_per_inch)

    @property
    def cm(self) -> float:
        return self._points / mm_per_cm / inch_per_mm / points_per_inch

    @classmethod
    def from_cm(cls, cm: float) -> 'CanvasUnit':
        return CanvasUnit(cm * mm_per_cm * inch_per_mm * points_per_inch)

    @property
    def px(self) -> float:
        return self._points / points_per_pixel

    @classmethod
    def from_px(cls, pixels: float) -> 'CanvasUnit':
        return CanvasUnit(pixels * points_per_pixel)

    @classmethod
    def from_unit(cls, value: float, unit: str) -> 'CanvasUnit':
        if unit == 'pt':
            return CanvasUnit.from_pt(value)
        elif unit == 'in':
            return CanvasUnit.from_in(value)
        elif unit == 'mm':
            return CanvasUnit.from_mm(value)
        elif unit == 'cm':
            return CanvasUnit.from_cm(value)
        elif unit == 'px':
            return CanvasUnit.from_px(value)
        raise Exception('Unknown unit')

    def __eq__(self, other: 'CanvasUnit'):
        if isinstance(other, CanvasUnit):
            return math.isclose(self.pt, other.pt, abs_tol=0.00001)
        else:
            return False

    def __add__(self, other):
        if isinstance(other, CanvasUnit):
            return CanvasUnit(self.pt + other.pt)
        if other == 0:
            return self
        raise NotImplementedError()

    def __radd__(self, other):
        if isinstance(other, CanvasUnit):
            return CanvasUnit(self.pt + other.pt)
        if other == 0:
            return self
        raise NotImplementedError()

    def __sub__(self, other):
        if isinstance(other, CanvasUnit):
            return CanvasUnit(self.pt - other.pt)
        raise NotImplementedError()

    def __mul__(self, x):
        return CanvasUnit(self.pt * x)

    def __truediv__(self, x):
        return CanvasUnit(self.pt / x)

    def __neg__(self):
        return CanvasUnit(-self.pt)
