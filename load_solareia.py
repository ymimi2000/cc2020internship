#!/usr/bin/env python
"""

"""
import csv
import logging
import os

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from solar.models.solar_util import SolarUtility

_LOGGER = logging.getLogger('django')


def _convert_to_bool(val):
    """Convert a 'Y' value to True and an 'N' to False."""
    vals = {
        'Y': True,
        'N': False,
    }
    return vals.get(val)


class Command(BaseCommand):
    help = 'Load solar EIA utility'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing solar EIA utility before loading data',
        )

    def handle(self, *args, **options):
        path = os.path.join(
            settings.BASE_DIR, 'windsolarsite/tests/EIAdata.csv'
        )
        with open(path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                solar_eia = SolarUtility.objects.get_or_create(
                    utilid=str(row[1]),
                    plant_code=int(row[2]),
                    ac_mw=float(row[3]),
                    dc_mw=str(row[4]),
                    single_axis=_convert_to_bool(str(row[5])),
                    dual_axis=_convert_to_bool(str(row[6])),
                    fixed=_convert_to_bool(str(row[7])),
                    east_west_fixed=_convert_to_bool(str(row[8])),
                    tilt_angle=str(row[9]),
                    lat=float(row[10]),
                    lon=float(row[11]),
                    zipcode=int(row[12]),
                    state=str(row[13]),
                    geoloc=Point(float(row[11]), float(row[10])),
                )
