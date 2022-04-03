def get_geodesic_test_cases():
    return [
        # Down the meridian
        {
            'lineString': [(20, 180), (15, 180)],
            'expectedGeomsBounds': [
                (15, 180, 20, 180)
            ]
        },
        {
            'lineString': [(-15, -180), (-20, -180)],
            'expectedGeomsBounds': [
                (-20, -180, -15, -180)
            ]
        },
        {
            'lineString': [(10, 180), (-10, -180)],
            'expectedGeomsBounds': [
                (0, 180, 10, 180),
                (-10, -180, 0, -180),
            ]
        },
        # Crossing the North Poles
        {
            'lineString': [(40, 10), (40, -170)],
            'expectedGeomsBounds': [
                (40, 10, 90, 10),
                (40, -170, 90, -170),
            ]
        },
        {
            'lineString': [(40, 20), (90, -160)],
            'expectedGeomsBounds': [
                (40, 20, 90, 20)
            ]
        },
        {
            'lineString': [(90, 30), (40, -150)],
            'expectedGeomsBounds': [
                (40, -150, 90, -150)
            ]
        },
        # Crossing the South Poles
        {
            'lineString': [(-40, 10), (-40, -170)],
            'expectedGeomsBounds': [
                (-90, 10, -40, 10),
                (-90, -170, -40, -170),
            ]
        },
        {
            'lineString': [(-40, 20), (-90, -160)],
            'expectedGeomsBounds': [
                (-90, 20, -40, 20)
            ]
        },
        {
            'lineString': [(-90, 30), (-40, -150)],
            'expectedGeomsBounds': [
                (-90, -150, -40, -150)
            ]
        },
        # Ambiguous crossing the poles (a point starting at the poles)
        {
            'lineString': [(90, 40), (-90, -100)],
            'expectedGeomsBounds': [
                (-90, -100, 90, 40)
            ]
        },
        # Un-ambiguous crossing the poles
        {
            'lineString': [(90, 50), (0, 0), (-90, -90)],
            'expectedGeomsBounds': [
                (-90, -90, 90, 50)
            ]
        },
        # This is a fun edge case: Ambiguous antipodes on the equator will
        # cause a line to be drawn that cross the North Pole. Technically
        # valid, but probably not expected. If the user of this function wants
        # a line that crosses the equator, they'll need to add an explicit
        # line segment that does that.
        {
            'lineString': [(0, 60), (0, -120)],
            'expectedGeomsBounds': [
                (-90, 60, 0, 60),
                (-90, -120, 0, -120)
            ]
        },
        # Crossing the poles, but hopefully the shortest way! In this case,
        # it should go up to the North Pole, then all the way down to the South
        # Pole, on the opposite longitude as the starting point.
        {
            'lineString': [(80, 50), (-75, -130)],
            'expectedGeomsBounds': [
                (80, 50, 90, 50),
                (-75, -130, 90, -130),
            ]
        },
        # California to Central Europe, which does not cross the anti-meridian.
        {
            'lineString': [(37, -122), (52, 13)],
            'expectedGeomsBounds': [
                (37, -122, 69.4, 13)
            ]
        },
        # Siberia to bottom of Chile, which crosses the anti-meridian. The
        # noteworthy thing about this path is that it goes up in latitude and
        # then goes down again.
        {
            'lineString': [(62, 129), (-57, -67)],
            'expectedGeomsBounds': [
                (62, 129, 64.7, 180),
                (-57, -180, 62.7, -67),
            ]
        },
        # Anchorage to Honolulu to Auckland to Sydney, which crosses the
        # anti-meridian from the eastern hemisphere to the western.
        {
            'lineString': [(61, -149), (21, -157), (-36, 174), (-33, 151)],
            'expectedGeomsBounds': [
                (-26.6, -180, 61, -149),
                (-36, 151, -26.6, 180),
            ]
        },
    ]
