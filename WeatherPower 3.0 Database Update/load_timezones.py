#!/usr/bin/env python
"""

"""
import json
import logging
import os

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand

from regions.models import Timezone

_LOGGER = logging.getLogger('django')
_GEO_FILE = os.path.join(settings.BASE_DIR, 'geojson/timezones.geojson')

class Command(BaseCommand):
    help = 'Load timezones'

    @staticmethod
    def _add_polygon(timezone, geometry):
        """Add a polygon to a Timezone's multipolygon geometry."""
        polygon = geometry['coordinates']
        if timezone.geometry:
            multipolygon = json.loads(timezone.geometry.geojson)
            multipolygon['coordinates'] += [polygon]
        else:
            multipolygon = {
                'type': 'MultiPolygon',
                'coordinates': [polygon]
            }
        timezone.geometry = GEOSGeometry(json.dumps(multipolygon))
        return timezone

    def _process_feature(self, feature):
        """Create or update a Timezone to include a polygon feature."""
        props = feature['properties']
        geometry = feature['geometry']
        (timezone, dummy_created) = Timezone.objects.get_or_create(
            name=props['TIMEZONE'],
        )
        timezone.symbol = props['SYMBOL']
        timezone.offset = props['GMT_OFFSET']
        timezone = self._add_polygon(timezone, geometry)
        timezone.save()
        print('Saved timezone feature for', timezone)

    def _add_data(self):
        """Load timezone data from the geojson file."""
        try:
            with open(_GEO_FILE) as file:
                geojson = json.load(file)
                features = geojson['features']
                print('Loading %s timezone polygons' % len(features))
                for feature in features:
                    self._process_feature(feature)

        except FileNotFoundError as error:
            _LOGGER.warning(error)

    def handle(self, *args, **options):
        self._add_data()
