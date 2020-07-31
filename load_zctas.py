#!/usr/bin/env python
"""

"""
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from regions.models import Egrid, State, Zcta
from windsolarApp.models import Solar

_SHAPEFILE = 'shapefiles/ZCTAs/cb_2017_us_zcta510_500k.shp'


class Command(BaseCommand):
    help = 'Load ZCTAs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing ZCTAs before loading data'
        )

    @staticmethod
    def _add_geometries():
        """Create records from a shapefile."""
        shapefile = os.path.join(settings.BASE_DIR, _SHAPEFILE)
        data_src = DataSource(shapefile)
        layer = data_src[0]
        print('Number of features:', len(layer))
        print('Spatial Reference System:\n', layer.srs)
        print('Fields:', layer.fields)
        mapping = {
            'id': 'ZCTA5CE10',
            'geometry': 'POLYGON',
        }
        lm = LayerMapping(Zcta, shapefile, mapping)
        lm.save(verbose=True, strict=True)

    @staticmethod
    def _add_data():
        """Copy data from the Solar table."""
        for zcta in Zcta.objects.only('id').iterator():
            try:
                solar = Solar.objects.get(zcta=zcta.id)
                zcta.res_solar_cap = solar.res_cap
                zcta.population = solar.population
                zcta.save()
                print('Saved data for', zcta)
            except Solar.DoesNotExist:
                pass

    @staticmethod
    def _add_relations():
        """Relate states to zctas.

        FIXME: It'd be better to use tabular data for this than a geo query.
        """
        zcta_index = 0
        for zcta in Zcta.objects.iterator():
            zcta_centroid = zcta.geometry.centroid

            try:
                state = State.objects.get(
                    geometry__intersects=zcta.geometry
                )
                zcta.state = state
                zcta.save()
                print('%s - Assigned %s to %s' % (zcta_index, zcta, state))

            # handle ZCTAs that fall along state boundaries
            except State.MultipleObjectsReturned:
                print('WARNING: Multiple states found for ZCTA %s' % zcta)
                try:
                    state = State.objects.get(
                        geometry__intersects=zcta_centroid
                    )
                    zcta.state = state
                    zcta.save()
                    print('%s - Assigned %s to %s' % (zcta_index, zcta, state))
                except State.DoesNotExist:
                    print('ERROR: %s\'s centroid is outside all states' % zcta)

            except State.DoesNotExist:
                print('WARNING: No state found for ZCTA %s' % zcta)

            try:
                egrid = Egrid.objects.get(geometry__intersects=zcta_centroid)
                zcta.egrid = egrid
                zcta.save()
                print('Assigned %s to %s' % (zcta, egrid))
            except Egrid.DoesNotExist:
                print('No eGRID fround for %s' % zcta)

            zcta_index += 1

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options.get('clear', False)
        if clear:
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE zcta')
            print('Cleared zcta table')
        self._add_geometries()
        self._add_data()
        self._add_relations()
