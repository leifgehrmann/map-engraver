def get_geodesic_test_cases():
    return [
        # Down the meridian
        # (10, ), (-10,-180)
        # Down the anti-meridian
        # (10,-180), (-10,180)
        # Crossing the poles
        {
            'lineString': [(40, 10), (40, -170)],
            'expectedLineStrings': [
                [(40, 10), (90, 10)],
                [(90, -170), (40, -170)]
            ]
        },
        {
            'lineString': [(40, 20), (90, -160)],
            'expectedLineStrings': [
                [(40, 20), (90, 20)],
            ]
        },
        {
            'lineString': [(90, 30), (40, -150)],
            'expectedLineStrings': [
                [(90, -130), (40, -130)],
            ]
        },
        # Crossing the poles, but which way?
        # (80,40), (-85, -140) -> ((80,40), (-90,40)), ((-90,-140), (-85, -140))
        # Cross the meridian
        # Cross the anti-meridian
        #
        # (90,40), (90, 40), (40, -90)

        # Siberia to bottom of Chile
        {
            'lineString': [(62, 129), (-57, -67)],
        },
        # California to Central Europe
        {
            'lineString': [(37, -122), (52, 13)],
        }
    ]
