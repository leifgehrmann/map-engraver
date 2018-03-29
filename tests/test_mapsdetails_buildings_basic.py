import math
from random import random

from shapely.geometry import Point

if False:

    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), 0, Point(1, 1)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), 0, Point(2, 2)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(1, 1), 0, Point(2, 2)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(1, 1), 0, Point(-2, -2)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(1, 1), math.pi / 2, Point(1, 2)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(1, 1), math.pi / 2, Point(2, 2)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), math.pi / 4, Point(math.sqrt(2), 0)))
    print(map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), math.pi / 4, Point(1, 0)))

    print("TEST", map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), math.pi / 4, Point(0, 2)))
    print("TEST", map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), math.pi / 4, Point(1, 3)))
    print("TEST", map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), math.pi / 4, Point(2, 4)))
    print("TEST", map.features.buildings.Basic.get_shortest_distance_between_point_and_line(Point(0, 0), math.pi / 4, Point(3, 5)))

    print("A", map.features.buildings.Basic.is_point_above_line(Point(2, 2), math.pi / 4, Point(1, 0)))
    print("B", map.features.buildings.Basic.is_point_above_line(Point(2, 2), math.pi / 4, Point(3, 1)))
    print("C", map.features.buildings.Basic.is_point_above_line(Point(2, 2), math.pi / 4, Point(4, 3)))

    print("D", map.features.buildings.Basic.is_point_above_line(Point(2, 2), math.pi / 4, Point(3, 4)))
    print("E", map.features.buildings.Basic.is_point_above_line(Point(2, 2), math.pi / 4, Point(1, 3)))
    print("F", map.features.buildings.Basic.is_point_above_line(Point(2, 2), math.pi / 4, Point(0, 1)))

    print("A", map.features.buildings.Basic.is_point_above_line(Point(2, 2), -math.pi / 4, Point(1, 0)))
    print("B", map.features.buildings.Basic.is_point_above_line(Point(2, 2), -math.pi / 4, Point(3, 1)))
    print("C", map.features.buildings.Basic.is_point_above_line(Point(2, 2), -math.pi / 4, Point(4, 3)))

    print("D", map.features.buildings.Basic.is_point_above_line(Point(2, 2), -math.pi / 4, Point(3, 4)))
    print("E", map.features.buildings.Basic.is_point_above_line(Point(2, 2), -math.pi / 4, Point(1, 3)))
    print("F", map.features.buildings.Basic.is_point_above_line(Point(2, 2), -math.pi / 4, Point(0, 1)))

    line_origin = Point(0,0)
    line_angle = math.pi/4

    bound = (1, 0, 2, 3)

    # Get the max distances for all 4 corners
    top_left = Point(bound[0], bound[1])
    top_right = Point(bound[2], bound[1])
    bottom_left = Point(bound[0], bound[3])
    bottom_right = Point(bound[2], bound[3])

    print(map.features.buildings.Basic.get_offset_between_point_and_line(line_origin, line_angle, top_left))
    print(map.features.buildings.Basic.get_offset_between_point_and_line(line_origin, line_angle, top_right))
    print(map.features.buildings.Basic.get_offset_between_point_and_line(line_origin, line_angle, bottom_right))
    print(map.features.buildings.Basic.get_offset_between_point_and_line(line_origin, line_angle, bottom_left))

if False:
    for x in [-math.pi/2, -math.pi/4, 0, math.pi/4, math.pi/2]:
        print("------------", x)
        if False:
            print("A = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), x, Point(-1, -2)))
            # print("  = ", features.buildings.Basic.is_point_above_line(Point(0, 0), x, Point( 0, -2)))
            print("B = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), x, Point(1, -2)))
            print("C = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), x, Point(1, 2)))
            # print("  = ", features.buildings.Basic.is_point_above_line(Point(0, 0), x, Point( 0,  2)))
            print("D = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), x, Point(-1, 2)))
        if False:
            print("A = ", map.features.buildings.Basic.get_offset_between_point_and_line(Point(0, 0), x, Point(-1, -2)))
            # print("  = ", features.buildings.Basic.get_offset_between_point_and_line(Point(0, 0), x, Point( 0, -2)))
            print("B = ", map.features.buildings.Basic.get_offset_between_point_and_line(Point(0, 0), x, Point(1, -2)))
            print("C = ", map.features.buildings.Basic.get_offset_between_point_and_line(Point(0, 0), x, Point(1, 2)))
            # print("  = ", features.buildings.Basic.get_offset_between_point_and_line(Point(0, 0), x, Point( 0,  2)))
            print("D = ", map.features.buildings.Basic.get_offset_between_point_and_line(Point(0, 0), x, Point(-1, 2)))

# From the range of the distances, we can now get an array of lines

if False:
    print("------------")
    print("A = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 2, Point(-1, -2)) == False)
    print("B = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 2, Point(1, -2)) == True)
    print("C = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 2, Point(1, 2)) == True)
    print("D = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 2, Point(-1, 2)) == False)

    print("A = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 4, Point(-1, -2)) == False)
    print("B = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 4, Point(1, -2)) == False)
    print("C = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 4, Point(1, 2)) == True)
    print("D = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), -math.pi / 4, Point(-1, 2)) == True)

    print("A = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), 0, Point(-1, -2)) == False)
    print("B = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), 0, Point(1, -2)) == False)
    print("C = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), 0, Point(1, 2)) == True)
    print("D = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), 0, Point(-1, 2)) == True)

    print("A = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 4, Point(-1, -2)) == False)
    print("B = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 4, Point(1, -2)) == False)
    print("C = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 4, Point(1, 2)) == True)
    print("D = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 4, Point(-1, 2)) == True)

    print("A = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 2, Point(-1, -2)) == True)
    print("B = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 2, Point(1, -2)) == False)
    print("C = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 2, Point(1, 2)) == False)
    print("D = ", map.features.buildings.Basic.is_point_above_line(Point(0, 0), math.pi / 2, Point(-1, 2)) == True)

if False:
    print("------------")
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), - math.pi, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), - 3 * math.pi / 4, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), - math.pi / 2, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), - math.pi / 4, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), 0, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), math.pi / 4, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), math.pi / 2, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), 3 * math.pi / 4, 2))
    print("x = ", map.features.buildings.Basic.get_intersection_point_of_line_with_y_axis(Point(0, 0), math.pi, 2))

if False:
    print("------------")
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(0, 0), math.pi / 4, [1., 0., 2., 3.]))
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(0, 0), math.pi / 8, [1., 0., 2., 3.]))
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(0, 0), 0, [1., 0., 2., 3.]))
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(0, 0), -math.pi / 8, [1., 0., 2., 3.]))
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(0, 0), -math.pi / 8 - math.pi, [1., 0., 2., 3.]))
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(0, 0), math.pi / 2, [1., 0., 2., 3.]))
    print("x = ", map.features.buildings.Basic.get_lines_within_box(Point(1.5, 0), math.pi / 2, [1., 0., 2., 3.]))

if False:
    print("------------")
    lines = map.features.buildings.Basic.get_lines_within_bounds(Point(0, 0), math.pi / 4, math.sqrt(2), [1, 1, 10, 10])
    for line in lines:
        print(line)

shortest_distance_func = map.features.buildings.Basic.get_shortest_distance_between_point_and_line

if True:
    for i in range(-10,10):
        print(math.isclose(shortest_distance_func(Point(i, i), 0, Point(i + random()*100, i + 1)), 1.0))
        print(math.isclose(shortest_distance_func(Point(i, i), 0, Point(i - random()*100, i + 1)), 1.0))
        print(math.isclose(shortest_distance_func(Point(i, i), 0.00000001, Point(i - random() * 100, i + 1)), 1.0, rel_tol=0.00001))
        print(math.isclose(shortest_distance_func(Point(i, i), math.pi / 2, Point(i + 1, i + 1)), 1.0))
        print(math.isclose(shortest_distance_func(Point(i, i), math.pi / 2, Point(i + 1, i + random() * 100)), 1.0))
    print(shortest_distance_func(Point(0, 0), 0, Point(4, 100)))
    print(shortest_distance_func(Point(0, 0), 0, Point(100, 4)))
    print(shortest_distance_func(Point(0, 0), math.pi/2, Point(4, 100)))
    print(shortest_distance_func(Point(0, 0), math.pi/2, Point(100, 4)))
    print(shortest_distance_func(Point(0, 0), math.pi / 2 * 2, Point(4, 100)))
    print(shortest_distance_func(Point(0, 0), math.pi / 2 * 2, Point(100, 4)))
    print(shortest_distance_func(Point(0, 0), math.pi / 2 * 3, Point(4, 100)))
    print(shortest_distance_func(Point(0, 0), math.pi / 2 * 3, Point(100, 4)))