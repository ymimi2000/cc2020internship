#!/usr/bin/env python
"""

"""
import json
import logging

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from solar.models.solar_util import SolarUtility
from windsolarApp.models import SolarUtils
from regions.models import MesoCell

_LOGGER = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Load solar utilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing solar utilities before loading data',
        )

    @staticmethod
    def _get_coordinates(lon, lat):
        geometry = {'type': 'Point', 'coordinates': [lon, lat]}
        return GEOSGeometry(json.dumps(geometry))

    @staticmethod
    def _convert_to_bool(val):
        """Convert a 'Y' value to True and an 'N' to False."""
        vals = {
            'Y': True,
            'N': False,
        }
        return vals.get(val)

    def _create_solar_utility(self, obj):
        (lon, lat) = (obj.grid_lon, obj.grid_lat)
        try:
            (solar, created) = SolarUtility.objects.get_or_create(id=obj.id)
            if created or not solar.meso_cell:
                meso_cell = MesoCell.objects.get(longitude=lon, latitude=lat)
                solar.ac_mw = obj.ac_mw
                solar.dc_mw = obj.dc_mw
                solar.tilt_angle = obj.tilt_angle
                solar.single_axis = self._convert_to_bool(obj.single_axis)
                solar.dual_axis = self._convert_to_bool(obj.dual_axis)
                solar.fixed = self._convert_to_bool(obj.fixed)
                solar.east_west_fixed = self._convert_to_bool(
                    obj.east_west_fixed
                )
                solar.meso_cell = meso_cell
                solar.save()
                print('Saved solar utility', solar)
            else:
                print('Skipping solar utility', solar)
        except MesoCell.DoesNotExist:
            _LOGGER.warning('No MesoCell found for solar utility %s', solar)

    def _copy_data(self):
        for obj in SolarUtils.objects.iterator():
            self._create_solar_utility(obj)

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options.get('clear', False)
        if clear:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    TRUNCATE TABLE solar_utility;
                """
                )
                print('Cleared solar_utility table')
        self._copy_data()
