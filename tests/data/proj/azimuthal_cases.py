def get_azimuthal_test_cases():
    return [
        {
            'proj4': '+proj=ortho +lon_0=0 +lat_0=0',
            'expectedProjBounds': (
                -6378136.3, -6356752.2, 6378136.3, 6356752.2
            ),
            'expectedWgs84Bounds': (-89.9, -89.9, 89.9, 89.9),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=0 +lat_0=0.1',
            'expectedProjBounds': (
                -6378136.3, -6356677.1, 6378136.3, 6356826.2
            ),
            'expectedWgs84Bounds': (-89.8, -180, 89.9, 180),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=0 +lat_0=20',
            'expectedProjBounds': (
                -6378121.9, -6345528.8, 6378121.9, 6372985.5
            ),
            'expectedWgs84Bounds': (-69.9, -180.0, 90.0, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=0 +lat_0=90',
            'expectedProjBounds': (
                -6378136.3, -6378136.3, 6378136.3, 6378136.3
            ),
            'expectedWgs84Bounds': (0.02, -180.0, 90.0, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=0 +lat_0=-90',
            'expectedProjBounds': (
                -6378136.3, -6378136.3, 6378136.3, 6378136.3
            ),
            'expectedWgs84Bounds': (-90.0, -180.0, -0.0, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=-90 +lat_0=0',
            'expectedProjBounds': (
                -6378136.3, -6356752.2, 6378136.3, 6356752.2
            ),
            'expectedWgs84Bounds': (-89.9, -179.9, 89.9, -0.1),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=135 +lat_0=0',
            'expectedProjBounds': (
                -6378136.3, -6356752.2, 6378136.3, 6356752.2
            ),
            'expectedWgs84Bounds': (-89.9, -180.0, 89.9, 180.0),
            'expectedWgs84GeomsCount': 2
        },
        {
            'proj4': '+proj=ortho +lon_0=180 +lat_0=0',
            'expectedProjBounds': (
                -6378136.3, -6356752.2, 6378136.3, 6356752.2
            ),
            'expectedWgs84Bounds': (-89.9, -180, 89.9, 180),
            'expectedWgs84GeomsCount': 2
        },
        {
            'proj4': '+proj=ortho +lon_0=180 +lat_0=0.1',
            'expectedProjBounds': (
                -6378136.3, -6356677.1, 6378136.3, 6356826.2
            ),
            'expectedWgs84Bounds': (-89.8, -180, 89.9, 180),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=-40 +lat_0=30',
            'expectedProjBounds': (
                -6378109.4, -6343600.7, 6378109.4, 6378136.3
            ),
            'expectedWgs84Bounds': (-59.9, -180.0, 90.0, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=ortho +lon_0=180 +lat_0=20',
            'expectedProjBounds': (
                -6378121.9, -6345528.8, 6378121.9, 6372985.5
            ),
            'expectedWgs84Bounds': (-69.9, -180.0, 90.0, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=geos +h=35785831.0 +lon_0=-60 +sweep=x',
            'expectedProjBounds': (
                -5434177.2, -5416234.9, 5434177.2, 5416234.9
            ),
            'expectedWgs84Bounds': (-81.3, -141.2, 81.3, 21.2),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=x',
            'expectedProjBounds': (
                -5434177.2, -5416234.9, 5434177.2, 5416234.9
            ),
            'expectedWgs84Bounds': (-81.3, -180.0, 81.3, 180.0),
            'expectedWgs84GeomsCount': 2
        },
        {
            'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=y',
            'expectedProjBounds': (
                -5434177.2, -5416234.9, 5434177.2, 5416234.9
            ),
            'expectedWgs84Bounds': (-81.3, -180.0, 81.3, 180.0),
            'expectedWgs84GeomsCount': 2
        },
        {
            'proj4': '+proj=nsper +h=3000000 +lat_0=-20 +lon_0=-60',
            'expectedProjBounds': (
                -2783092.3, -2783092.3, 2783092.3, 2783092.3
            ),
            'expectedWgs84Bounds': (-67.1, -111.2, 27.1, -8.7),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=nsper +h=3000000 +lat_0=-20 +lon_0=145',
            'expectedProjBounds': (
                -2783092.3, -2783092.3, 2783092.3, 2783092.3
            ),
            'expectedWgs84Bounds': (-67.1, -180.0, 27.1, 180.0),
            'expectedWgs84GeomsCount': 2
        },
        {
            'proj4': '+proj=nsper +h=3000000 +lat_0=-80 +lon_0=145',
            'expectedProjBounds': (
                -2783092.3, -2783092.3, 2783092.3, 2783092.3
            ),
            'expectedWgs84Bounds': (-90.0, -180.0, -32.8, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=tpers +h=5500000 +lat_0=40',
            'expectedProjBounds': (
                -3500814.2, -3500814.2, 3500814.2, 3500814.2
            ),
            'expectedWgs84Bounds': (-17.4, -180.0, 90.0, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=tpers +h=5500000 +lat_0=-40',
            'expectedProjBounds': (
                -3500814.2, -3500814.2, 3500814.2, 3500814.2
            ),
            'expectedWgs84Bounds': (-90.0, -180.0, 17.4, 180.0),
            'expectedWgs84GeomsCount': 1
        },
        {
            'proj4': '+proj=tpers +h=5500000 +lat_0=30 +lon_0=-120 +tilt=30',
            'expectedProjBounds': (
                -3763998.6, -6378136.2, 3763998.6, 2956066.6
            ),
            'expectedWgs84Bounds': (-27.3, -180.0, 87.5, 180.0),
            'expectedWgs84GeomsCount': 2
        },
    ]
