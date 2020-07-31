#!/usr/bin/env python
"""

"""
import json

from django.core.management.base import BaseCommand
from osgeo import ogr


class Command(BaseCommand):
    """Convert shapefile to geojson.

    Example: python manage.py create_geojson shapefiles/tz/timeznp020.shp
    geojson/timezones.geojson
    """

    help = 'Convert shapefile to geojson'

    def add_arguments(self, parser):
        parser.add_argument('src', type=str, help='shapfile')
        parser.add_argument('output', type=str, help='geojson file')

    @staticmethod
    def _shapefile_to_geojson(src, output):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        data_source = driver.Open(src, 0)

        fc = {
            'type': 'FeatureCollection',
            'features': []
        }

        lyr = data_source.GetLayer(0)
        for feature in lyr:
            fc['features'].append(feature.ExportToJson(as_object=True))

        with open(output, 'w') as f:
            json.dump(fc, f)

    def handle(self, *args, **kwargs):
        shp_file = kwargs['src']
        geo_file = kwargs['output']
        self._shapefile_to_geojson(shp_file, geo_file)
