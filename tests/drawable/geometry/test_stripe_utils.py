import unittest

from map_engraver.drawable.geometry.stripe_utils import \
    create_polygon_from_stripe_lines_x_bounded


class TestStripeUtils(unittest.TestCase):
    def test_create_polygon_from_stripe_lines_x_bounded(self):
        # Horizontal stripe
        self.assertEqual(
            [(-1, 1), (3, 1), (3, 2), (-1, 2), (-1, 1)],
            list(create_polygon_from_stripe_lines_x_bounded(
                ((0, 1), (1, 0)),
                ((0, 2), (1, 0)),
                (-1, -1, 3, 3 )
            ).exterior.coords)
        )

        # Vertical stripe
        self.assertEqual(
            [(1, -1), (1, 3), (2, 3), (2, -1), (1, -1)],
            list(create_polygon_from_stripe_lines_x_bounded(
                ((1, 1), (0, 1)),
                ((2, 1), (0, 1)),
                (-1, -1, 3, 3)
            ).exterior.coords)
        )
