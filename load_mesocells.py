#!/usr/bin/env python
"""

"""
from django.core.management.base import BaseCommand
from django.db import connection

from regions.models import (
    BlockGroup, County, Dma, Egrid, MesoCell, State, Timezone, Zcta
)


class Command(BaseCommand):
    help = 'Load MESO cells'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing MESO cells before loading data'
        )

    @staticmethod
    def _copy_data():
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO meso_cell(
                    latitude,
                    longitude,
                    area,
                    population,
                    res_cap
                )
                SELECT
                    CAST(latitude AS float),
                    CAST(longitude AS float),
                    area,
                    population,
                    res_cap
                FROM cells
            """)
        print('Copied data from old table')

    @staticmethod
    def _create_points():
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE meso_cell
                SET coordinates = ST_SetSRID(ST_MakePoint(longitude, latitude),
                                             4326);
            """)
        print('Added coordinates')

    @staticmethod
    def _create_geometry():
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE meso_cell
                SET geometry = ST_SetSRID(
                    ST_MakeEnvelope(
                        longitude - 0.025,
                        latitude - 0.025,
                        longitude + 0.025,
                        latitude + 0.025
                    ), 4326);
            """)
        print('Added geometry')

    @staticmethod
    def _relate_regions():

        for timezone in Timezone.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=timezone.geometry
            )
            mesocells.update(timezone=timezone)
            print('Assigned %s mesocells to timezone %s'
                  % (mesocells.count(), timezone))

        for state in State.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=state.geometry
            )
            mesocells.update(state=state)
            print('Assigned %s mesocells to state %s'
                  % (mesocells.count(), state))

        for county in County.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=county.geometry
            )
            mesocells.update(county=county)
            print('Assigned %s mesocells to county %s'
                  % (mesocells.count(), county))

        for cd in CongressionalDistrict.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=cd.geometry
            )
            mesocells.add(congressional_district=cd)
            print('Assigned %s mesocells to cd %s'
                  % (mesocells.count(), cd))

        for dma in Dma.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=dma.geometry
            )
            mesocells.update(dma=dma)
            print('Assigned %s mesocells to dma %s'
                  % (mesocells.count(), dma))

        for egrid in Egrid.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=egrid.geometry
            )
            mesocells.update(egrid=egrid)
            print('Assigned %s mesocells to egrid %s'
                  % (mesocells.count(), egrid))

        zcta_index = 0
        for zcta in Zcta.objects.iterator():
            mesocells = MesoCell.objects.only('geometry').filter(
                centroid__intersects=zcta.geometry
            )
            mesocells.update(zcta=zcta)
            print('%s - Assigned %s mesocells to zcta %s'
                  % (zcta_index, mesocells.count(), zcta))
            zcta_index += 1

        blockgroup_index = 0
        for blockgroup in BlockGroup.objects.iterator():
            mesocells = MesoCell.objects.filter(
                geometry__intersects=blockgroup.geometry
            )
            for mesocell in mesocells:
                mesocell.blockgroups.add(blockgroup)
            print('%s - Assigned %s mesocells to blockgroup %s'
                  % (blockgroup_index, mesocells.count(), blockgroup))
            blockgroup_index += 1

    def handle(self, *args, **options):
        clear = options.get('clear', False)
        if clear:
            with connection.cursor() as cursor:
                cursor.execute("""
                    TRUNCATE TAB meso_cell CASCADE;
                    ALTER SEQUENCE meso_cell_id_seq RESTART WITH 1;
                """)
            print('Cleared meso_cell table and reset autoincrement sequence')

        self._copy_data()
        self._create_points()
        self._create_geometry()
        self._relate_regions()
