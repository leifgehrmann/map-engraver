import unittest

from tests.utils import svg_has_tag, svg_has_style_attr


real_svg = """<?xml version="1.0" encoding="UTF-8"?> <svg xmlns="http://www.w3.org/2000/svg" 
        xmlns:xlink="http://www.w3.org/1999/xlink" width="100pt" height="100pt" viewBox="0 0 100 100"> <path 
        fill="none" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round" stroke="rgb(100%, 0%, 
        0%)" stroke-opacity="1" stroke-miterlimit="10" d="M 45.5 0.898438 L 45.398438 1.300781 L 45.398438 1.601562 L 
        45.300781 1.699219 L 45.300781 2.101562 L 45.199219 2.199219 L 45.199219 2.601562 L 45.101562 2.699219 L 
        45.101562 3.101562 L 44.898438 3.601562 L 44.898438 4 L 44.800781 4.101562 L 44.800781 4.5 L 44.601562 5 L 
        44.601562 5.398438 L 44.5 5.5 L 44.5 5.898438 L 44.398438 6 L 44.398438 6.398438 L 44.199219 7.101562 L 
        44.199219 7.300781 L 44.101562 7.398438 M 50.898438 0.898438 L 50.800781 1.5 L 50.699219 1.601562 L 50.699219 
        2 L 50.601562 2.101562 L 50.601562 2.5 L 50.101562 3.699219 L 49.300781 3 L 48.898438 2.800781 L 48.300781 
        2.800781 L 47.800781 3 L 47.398438 3.199219 L 46.699219 4 L 46.699219 4.199219 L 46.300781 4.898438 L 
        46.300781 5.5 L 46.199219 5.601562 L 46.199219 6.398438 L 46.300781 6.800781 L 46.800781 7.398438 L 47.199219 
        7.5 L 48.398438 7.398438 L 49.601562 6.699219 L 49.5 7.398438 L 49 7 M 14.101562 1 L 14.101562 7.300781 M 
        16.101562 1 L 16.101562 7.300781 M 36.101562 1 L 35.5 2.101562 L 35.5 2.300781 L 35.398438 2.5 L 34.898438 
        3.398438 L 34.898438 3.601562 L 34.800781 3.800781 L 34.601562 4.101562 L 34.5 4.300781 L 34.5 4.5 L 
        34.199219 5 L 34.199219 5.199219 L 34.101562 5.398438 L 33.601562 6.5 L 32.898438 7.101562 M 32.199219 
        1.101562 L 31.800781 1.398438 L 31.5 1.800781 L 31.199219 2.398438 L 31.199219 2.601562 L 31.101562 2.800781 
        L 29.300781 6.398438 L 29 6.699219 L 28.601562 6.898438 L 28.398438 6.5 L 28.398438 5 L 28.300781 1.199219 M 
        1.300781 1.199219 L 1.398438 4 L 1.300781 7.199219 M 6 1.199219 L 5.898438 4 L 6 7.199219 M 32.199219 
        1.300781 L 32.398438 2 L 32.5 2.101562 L 32.5 3.601562 L 32.601562 3.699219 L 32.601562 5.101562 L 32.699219 
        5.199219 L 32.699219 6.601562 L 32.800781 6.699219 L 32.898438 6.800781 L 33 6.898438 M 7.800781 5 L 7.898438 
        4.199219 L 8.199219 3.601562 L 8.699219 3.101562 L 9.398438 2.800781 L 10.101562 2.800781 L 10.601562 3 L 
        11.300781 3.5 L 11.5 4 L 11.601562 4.898438 L 11.398438 5.101562 L 7.898438 5.101562 L 7.800781 5.199219 L 
        7.800781 5.5 L 7.898438 6.300781 L 8.199219 6.800781 L 9 7.5 L 9.699219 7.601562 L 10.398438 7.5 L 10.800781 
        7.300781 L 11.5 6.5 M 19.199219 2.800781 L 20.199219 2.800781 L 20.699219 3 L 21.300781 3.5 L 21.398438 
        3.898438 L 21.5 4 L 21.601562 4.300781 L 21.699219 4.699219 L 21.699219 5.5 L 21.601562 5.898438 L 21.398438 
        6.5 L 21.199219 6.898438 L 20.398438 7.5 L 19.601562 7.601562 L 18.699219 7.398438 L 18.199219 6.898438 L 
        17.800781 6.199219 L 17.699219 5.199219 L 17.800781 4.800781 L 17.800781 4.300781 L 18 3.800781 L 18.699219 3 
        L 19.199219 2.800781 M 38.300781 2.800781 L 39.601562 2.898438 L 40.101562 3.398438 L 40.300781 3.800781 L 
        40.300781 4.898438 L 40 5.898438 L 39.800781 6.300781 L 39.5 6.699219 L 38.898438 7.300781 L 38.5 7.5 L 
        37.601562 7.601562 L 37.101562 7.5 L 36.300781 6.898438 L 36.300781 6.5 L 36.199219 6.398438 L 36.199219 
        5.398438 L 36.300781 5.300781 L 36.300781 4.898438 L 36.5 4.398438 L 36.898438 3.699219 L 37.699219 3 L 
        38.300781 2.800781 M 42.699219 3.398438 L 42 3.800781 L 42.101562 3 L 42.601562 3.398438 L 43.398438 3 L 
        43.699219 3 M 50.101562 3.699219 L 50.101562 4.699219 L 50 4.800781 L 50 5.398438 L 49.898438 5.800781 L 
        49.800781 5.898438 L 49.699219 6.300781 L 49.699219 6.601562 M 41.898438 3.898438 L 41.800781 4.5 L 41.601562 
        5 L 41.601562 5.398438 L 41.5 5.5 L 41.5 5.898438 L 41.398438 6 L 41.398438 6.398438 L 41.199219 7.101562 L 
        41.199219 7.300781 L 41.101562 7.398438 M 1.398438 4 L 5.898438 4 M 28.601562 6.898438 L 28.601562 7.199219 " 
        transform="matrix(1, 0, 0, 1, 10, 10)"/> </svg> """


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
