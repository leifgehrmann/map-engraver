from typing import List, Dict, Tuple

from map_engraver.data.osm import Node


def piece_together_ways(
        way_refs: List[str],
        way_nodes: Dict[str, List[Node]],
        way_start_nodes: Dict[str, Node],
        way_end_nodes: Dict[str, Node]
) -> Tuple[Dict[str, List[Node]], Dict[str, List[Node]]]:
    output_ways = dict()
    way_ref_index_1 = 0
    while way_ref_index_1 < len(way_refs):
        # print("----")
        way_ref_1 = way_refs[way_ref_index_1]
        # print("ref1 " + str(way_ref_1))

        # way is closed, so delete this way from the list of ways to
        # process and continue to the next way
        if way_end_nodes[way_ref_1] == way_start_nodes[way_ref_1]:
            # print(
            # "Closed way!",
            # way_end_nodes[way_ref_1],
            # way_start_nodes[way_ref_1]
            # )
            output_ways[way_ref_1] = way_nodes[way_ref_1]

            del way_refs[way_ref_index_1]
            del way_nodes[way_ref_1]
            del way_start_nodes[way_ref_1]
            del way_end_nodes[way_ref_1]
            continue

        # go through all other ways (excluding self)
        way_ref_index_2 = 0
        while way_ref_index_2 < len(way_refs):
            way_ref_2 = way_refs[way_ref_index_2]
            if way_ref_1 == way_ref_2:
                way_ref_index_2 += 1
                continue

            # print("ref2 " + str(way_ref_2))

            # if the end node of the current way is connected to the start
            # node of the other way
            if way_end_nodes[way_ref_1] == way_start_nodes[way_ref_2]:
                # remove the first node of the other way to ensure we don't
                # have redundant nodes and add it to the end of the current
                # way
                way_nodes_2 = way_nodes[way_ref_2][1:]
                way_nodes[way_ref_1].extend(way_nodes_2)

                # updated the linked list attributes
                way_end_nodes[way_ref_1] = way_end_nodes[way_ref_2]

                # Delete any mention of this way entirely!
                del way_nodes[way_ref_2]
                del way_start_nodes[way_ref_2]
                del way_end_nodes[way_ref_2]
                del way_refs[way_ref_index_2]
                # if the index of the other way is behind the current way
                # index, make sure to change the index because the other
                # way was removed from the list!
                way_ref_index_2 -= 1
                if way_ref_index_1 > way_ref_index_2:
                    way_ref_index_1 -= 1

                # Break out of this loop. The current way should be
                # reprocessed in an attempt to discover more ways to
                # connect / discover that it is a closed loop
                break

            # otherwise proceed to the next way in the list
            way_ref_index_2 += 1

        # Only proceed onto the next item if we have properly gone through
        # all the other ways
        if way_ref_index_2 == len(way_refs):
            way_ref_index_1 += 1

    return way_nodes, output_ways
