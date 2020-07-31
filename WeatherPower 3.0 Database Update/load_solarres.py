#!/usr/bin/env python
"""

"""
import csv
import logging
import os

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from solar.models.solar_res import SolarRes


_LOGGER = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Load solar residential'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing solar residential before loading data',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'solar/ResidentialData.csv')
        with open(path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                solarr = SolarRes.objects.create(
                    tract_id=float(row[0]),
                    tract_LAT=float(row[2]),
                    tract_LON=float(row[3]),
                    dc_kw =float(row[1]),
                    source=str(row[4]),
                )

        path2 = os.path.join(settings.BASE_DIR, 'solar/HawaiiCT.csv')
        with open(path2, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if float(row[5]) != 0.0:
                    solarr = SolarRes.objects.create(
                        tract_id=float(row[2]),
                        tract_LAT=float(row[3]),
                        tract_LON=float(row[4]),
                        dc_kw=float(row[5]),
                        source=str(row[6]),
                    )

        for solarresi in SolarRes.objects.all():
            solarresi.geoloc = Point(solarresi.tract_LON, solarresi.tract_LAT)
            solarresi.save()

        path3 = os.path.join(settings.BASE_DIR, 'solar/TractState.csv')
        with open(path3, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                try:
                    solarr = SolarRes.objects.get(tract_id=float(row[0]))
                    solarr.state = str(row[2])
                    solarr.save()
                except Exception:
                    pass
