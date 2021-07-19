from mapengraver.data.osm import Osm


def get_nodes_for_way(osm: Osm, way_ref: str):
    return [osm.nodes[node_ref] for node_ref in osm.ways[way_ref].node_refs]
