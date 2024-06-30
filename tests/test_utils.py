import unittest

from tests.utils import svg_has_tag, svg_has_style_attr


real_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100pt" height="100pt"
     viewBox="0 0 100 100">
    <path
        fill="none"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke="rgb(100%, 0%, 0%)"
        stroke-opacity="1"
        stroke-miterlimit="10"
        d="M 30 30 L 70 30 L 70 70 L 30 70"
        transform="matrix(1, 0, 0, 1, 10, 10)"
    />
</svg> """


class TestUtils(unittest.TestCase):
    def test_svg_has_tag(self):
        svg = '<myElements><myElement myAttr="myValue"/></myElements>'
        assert svg_has_tag(svg, 'myElements')
        assert svg_has_tag(svg, 'myElement')
        assert not svg_has_tag(svg, 'myElem')
        assert not svg_has_tag(svg, 'missingElement')

    def test_svg_has_tag_real_svg(self):
        assert svg_has_tag(real_svg, 'path')
        assert svg_has_tag(real_svg, 'svg')
        assert not svg_has_tag(real_svg, 'circle')

    def test_svg_has_style_attr(self):
        svg = '<myElements><myElement myAttr="myValue"/></myElements>'
        assert svg_has_style_attr(svg, 'myElement', 'myAttr')
        assert not svg_has_style_attr(svg, 'myElem', 'myAttr')
        assert not svg_has_style_attr(svg, 'missingElement', 'myAttr')
        svg = '<path fill="none" x="20%" />'
        assert svg_has_style_attr(svg, 'path', 'fill', 'none')
        for case in [
            '<ele attr="m(0.0,2,43)"></ele>',
            '<ele style="attr:m(0.0,2,43)"></ele>',
            '<x><ele attr="m(0.0,2,43)"></ele></x>',
            '<x><ele attr="m(0.0,2,43)"/></x>',
            '<x><ele a="c" attr="m(0.0,2,43)" b="xyz"></ele></x>',
        ]:
            assert svg_has_style_attr(case, 'ele', 'attr')
            assert svg_has_style_attr(case, 'ele', 'attr', 'm(0.0,2,43)')
            assert svg_has_style_attr(case, 'ele', 'attr', r'.*', escape=False)
            assert not svg_has_style_attr(case, 'ele', 'attr', 'm(0.1,2,43)')
            assert not svg_has_style_attr(case, 'ele', 'attr2', 'm(0.0,2,43)')

    def test_svg_has_style_attr_real_svg(self):
        assert svg_has_style_attr(real_svg, 'path', 'fill', 'none')
        assert svg_has_style_attr(real_svg, 'svg', 'width', '100pt')
        assert not svg_has_style_attr(real_svg, 'path', 'missing-prop', '0.5')
        assert not svg_has_style_attr(real_svg, 'path', 'fill', 'fakeValue')
