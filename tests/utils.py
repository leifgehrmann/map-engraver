import re
import xml.etree.ElementTree as Et
from typing import Optional, Iterator

ns_array = {
    'svg': 'http://www.w3.org/2000/svg',
    'xlink': 'http://www.w3.org/1999/xlink'
}


def svg_has_tag(svg: str, tag: str) -> bool:
    el = Et.fromstring(svg)
    print(el.tag)
    if el.tag == tag or el.tag == '{' + ns_array['svg'] + '}' + tag:
        return True
    if el.find(tag, ns_array) is not None:
        return True
    if el.find('svg:' + tag, ns_array) is not None:
        return True
    return False


def _get_style_attr_value(style: str, attr: str) -> Optional[str]:
    for style_prop in style.split(';'):
        if style_prop.split(':')[0] == attr:
            return style_prop.split(':')[1]
    return None


def _get_attr_value(el: Et.Element, attr: str) -> Optional[str]:
    if attr in el.attrib:
        return el.attrib[attr]
    if 'style' in el.attrib:
        return _get_style_attr_value(el.attrib['style'], attr)
    return None


def _svg_get_matches(
    svg: str,
    tag: str,
    attr: str,
    value: Optional[str] = None,
    escape: bool = True
) -> Iterator[Et.Element]:
    el = Et.fromstring(svg)
    matches = []
    matches.extend(el.findall(tag, ns_array))
    matches.extend(el.findall('svg:' + tag, ns_array))
    if value is not None and escape:
        value = re.escape(value)
    if el.tag == tag or el.tag == '{' + ns_array['svg'] + '}' + tag:
        matches.append(el)
    for match in matches:
        match_value = _get_attr_value(match, attr)
        if match_value is None:
            continue
        if value is None:
            yield match
        if re.match(value, match_value) is not None:
            yield match


def svg_has_style_attr(
    svg: str,
    tag: str,
    attr: str,
    value: Optional[str] = None,
    escape: bool = True
) -> bool:
    for _ in _svg_get_matches(svg, tag, attr, value, escape=escape):
        return True
    return False


def svg_count_style_attr(
    svg: str,
    tag: str,
    attr: str,
    value: Optional[str] = None,
    escape: bool = True
) -> int:
    return len(list(_svg_get_matches(svg, tag, attr, value, escape=escape)))
