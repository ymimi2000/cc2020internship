#!/usr/bin/env python
"""

"""
import logging
import os
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
import zipfile

from django.core.management.base import BaseCommand
from django.db import transaction

from regions.models import Egrid, State, TemporaryRegion
from windsolarsite.utils import check_region_count


_SHAPEFILE = 'eGRID2018 Subregions.shp'
_ZIP_FILE = 'egrid2018_subregions.zip'
_DOWNLOAD_URL = (
    f'https://www.epa.gov/sites/production/files/2020-03/{_ZIP_FILE}'
)

_LOGGER = logging.getLogger('django')
_LOGGER.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Load eGRIDs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing eGRIDs before loading data',
        )
        parser.add_argument(
            '--relate',
            action='store_true',
            dest='relate',
            help='relate eGRIDs to states',
        )

    def _download_shapefile(self, url, tmpdirname):
        zip_file = os.path.join(tmpdirname, _ZIP_FILE)
        filehandle, _ = urlretrieve(url, filename=zip_file)
        with zipfile.ZipFile(filehandle, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)

    def _create_tmp_regions(self, tmpdirname):
        """Create TemporaryRegions from eGRID shapefile."""
        self._download_shapefile(_DOWNLOAD_URL, tmpdirname)
        shapefile = os.path.join(tmpdirname, _SHAPEFILE)
        mapping = {
            'name': 'ZipSubregi',
            'geometry': 'POLYGON',
        }
        TemporaryRegion.objects.create_from_shapefile(shapefile, mapping)

    def _create_egrids(self, tmpdirname):
        """Create Egrids from TemporaryRegions."""
        self._create_tmp_regions(tmpdirname)
        check_region_count(Egrid)

        for tmp_region in TemporaryRegion.objects.iterator():
            id = tmp_region.name
            try:
                _LOGGER.info(f'Adding geometry to {id}')
                egrid, dummy_created = Egrid.objects.get_or_create(id=id)
                egrid.geometry = tmp_region.geometry
                egrid.save()
            except Egrid.DoesNotExist:
                _LOGGER.error(f'Skipping geometry for {id}')

    @staticmethod
    def _add_relations():
        """Relate eGRIDs to states."""
        for egrid in Egrid.objects.only('id').iterator():
            _LOGGER.info(f'Started processing eGRID {egrid}')
            states = State.objects.filter(
                geometry__intersects=egrid.geometry
            ).only('id')
            for state in states:
                egrid.states.add(state)
                _LOGGER.info(f'Assigned eGRID {egrid} to {state}')

            _LOGGER.info(f'Finished processing eGRID {egrid}')

    @transaction.atomic  # rollback changes if anything goes wrong
    def handle(self, *args, **options):
        clear = options.get('clear', False)
        relate = options.get('relate', False)

        if clear:
            Egrid.objects.all().delete()

        tmpdir = TemporaryDirectory()
        with tmpdir as tmpdirname:
            self._create_egrids(tmpdirname, relate)

        if relate:
            self._add_relations()
