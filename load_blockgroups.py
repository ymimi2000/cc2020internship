#!/usr/bin/env python
"""

"""
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from django.db import connection

from regions.models import BlockGroup, County, State

_SHAPEFILE = 'shapefiles/blockgroups/tl_2017_USA_bg.shp'


class Command(BaseCommand):
    help = 'Load Census block groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing block groups before loading data'
        )

    @staticmethod
    def _add_geometries():
        """Create records from a shapefile."""
        shapefile = os.path.join(settings.BASE_DIR, _SHAPEFILE)
        data_src = DataSource(shapefile)
        layer = data_src[0]
        print('Number of features:', len(layer))
        print('Spatial Reference System:\n', layer.srs)
        mapping = {
            'id': 'GEOID',
            'state_fips': 'STATEFP',
            'county_fips': 'COUNTYFP',
            'census_tract': 'TRACTCE',
            'block_id': 'BLKGRPCE',
            'geometry': 'POLYGON',
        }
        lm = LayerMapping(BlockGroup, shapefile, mapping)
        lm.save(verbose=True, strict=True, step=1000)

    @staticmethod
    def _add_relations():
        """Relate block groups to states and counties."""
        for county in County.objects.defer('geometry').iterator():
            block_groups = BlockGroup.objects.filter(
                state_fips=county.state_fips,
                county_fips=county.county_fips
            )
            block_groups.update(county=county)
            print('Saved block groups for', county.name_lsad)
        for state in State.objects.defer('geometry').iterator():
            block_groups = BlockGroup.objects.filter(state_fips=state.fips)
            block_groups.update(state=state)
            print('Saved block groups for %s' % state)

    def handle(self, *args, **options):
        clear = options.get('clear', False)
        if clear:
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE blockgroup')
            print('Cleared blockgroup table')
        self._add_geometries()
        self._add_relations()
