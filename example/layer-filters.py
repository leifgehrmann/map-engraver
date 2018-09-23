def all_buildings_ways(osm_map):
    buildings = {
        way_ref: way for
        way_ref, way in
        osm_map.ways.items() if
        ("building" in way.tags)
    }

    return buildings


def all_buildings_rel(osm_map):
    buildings_rel = {
        relation_ref: relation for
        relation_ref, relation in
        osm_map.relations.items() if
        ("building" in relation.tags)
    }

    return buildings_rel


def all_buildings(osm_map):
    return {
        "ways": all_buildings_ways(osm_map),
        "relations": all_buildings_rel(osm_map)
    }


def all_barriers(osm_map):
    return {
        'ways': {
            way_ref: way for
            way_ref, way in
            osm_map.ways.items() if
            ("barrier" in way.tags)
        }
    }


def all_railways(osm_map):
    ways = {
        way_ref: way for
        way_ref, way in
        osm_map.ways.items() if
        ("railway" in way.tags and
         way.tags["railway"] == "rail" and
         "tunnel" not in way.tags and
         "service" not in way.tags)
    }

    return {"ways": ways}


def all_road_names(osm_map):
    ways = {
        way_ref: way for
        way_ref, way in
        osm_map.ways.items() if
        ("highway" in way.tags and
         (way.tags["highway"] == "motorway" or
          way.tags["highway"] == "trunk" or
          way.tags["highway"] == "primary" or
          way.tags["highway"] == "secondary" or
          way.tags["highway"] == "tertiary" or
          way.tags["highway"] == "residential" or
          way.tags["highway"] == "motorway_link" or
          way.tags["highway"] == "trunk_link" or
          way.tags["highway"] == "primary_link" or
          way.tags["highway"] == "secondary_link" or
          way.tags["highway"] == "tertiary_link" or
          way.tags["highway"] == "unclassified" or
          (way.tags["highway"] == "service" and "name" in way.tags)))
    }

    return {"ways": ways}


def all_nature_areas(osm_map):
    ways = {
        way_ref: way for
        way_ref, way in
        osm_map.ways.items() if
        (
            ("leisure" in way.tags and (
                way.tags["leisure"] == "garden" or
                way.tags["leisure"] == "park" or
                way.tags["leisure"] == "recreation_ground" or
                way.tags["leisure"] == "common"
            )) or
            ("landuse" in way.tags and
             (
                 way.tags["landuse"] == "grass" or
                 way.tags["landuse"] == "forest"
             )) or
            ("natural" in way.tags and
             way.tags["natural"] == "wood")
        )
    }

    return {"ways": ways}


def all_riverbanks(osm_map):
    ways = {
        way_ref: way for
        way_ref, way in
        osm_map.ways.items() if
        ("waterway" in way.tags and
         way.tags["waterway"] == "riverbank")
    }

    relations = {
        relation_ref: relation for
        relation_ref, relation in
        osm_map.relations.items() if
        ("waterway" in relation.tags and
         relation.tags["waterway"] == "riverbank")
    }

    return {
        "ways": ways,
        "relations": relations
    }


def all_lakes(osm_map):
    ways = {
        way_ref: way for
        way_ref, way in
        osm_map.ways.items() if
        ("natural" in way.tags and
         way.tags["natural"] == "water")
    }

    relations = {
        relation_ref: relation for
        relation_ref, relation in
        osm_map.relations.items() if
        ("natural" in relation.tags and
         relation.tags["natural"] == "water")
    }

    return {
        "ways": ways,
        "relations": relations
    }
