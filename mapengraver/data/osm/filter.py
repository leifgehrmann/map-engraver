from typing import Callable

from mapengraver.data.osm import Osm, Element
from mapengraver.data.osm import OsmSubset


def filter_elements(
        osm: Osm,
        filter_function: Callable[[Osm, Element], bool],
        filter_nodes: bool = True,
        filter_ways: bool = True,
        filter_relations: bool = True,
) -> OsmSubset:
    nodes = {}
    ways = {}
    relations = {}

    if filter_nodes:
        nodes = {
            ref: element for ref, element in osm.nodes.items() if
            filter_function(osm, element)
        }

    if filter_ways:
        ways = {
            ref: element for ref, element in osm.ways.items() if
            filter_function(osm, element)
        }

    if filter_relations:
        relations = {
            ref: element for ref, element in osm.relations.items() if
            filter_function(osm, element)
        }

    return OsmSubset(
        nodes=nodes,
        ways=ways,
        relations=relations
    )
