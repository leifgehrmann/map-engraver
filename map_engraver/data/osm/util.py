from typing import List

from map_engraver.data.osm import Osm, Node


def get_nodes_for_way(osm: Osm, way_ref: str) -> List[Node]:
    return [osm.nodes[node_ref] for node_ref in osm.ways[way_ref].node_refs]
