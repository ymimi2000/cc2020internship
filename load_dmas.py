#!/usr/bin/env python
"""

"""
import logging
import os
from tempfile import TemporaryDirectory

from django.core.management.base import BaseCommand
from django.db import transaction

from regions.models import Dma, Egrid, State, TemporaryRegion
from windsolarsite.utils import check_region_count

_SHAPEFILE = 'DMA_2016_Geographic.shp'
_SHP_PATH = os.path.join('shapefiles/DMAs', _SHAPEFILE)

_LOGGER = logging.getLogger('django')
_LOGGER.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Load DMAs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing DMAs before loading data'
        )
        parser.add_argument(
            '--relate',
            action='store_true',
            dest='relate',
            help='relate DMAs to states and eGRIDs',
        )

    def _create_tmp_regions(self, tmpdirname):
        """Create TemporaryRegions from DMA shapefile."""
        mapping = {
            'name': 'NAME',
            'geometry': 'POLYGON',
        }
        TemporaryRegion.objects.create_from_shapefile(_SHP_PATH, mapping)

    def _create_dmas(self, tmpdirname):
        """Create Dmas from TemporaryRegions."""
        self._create_tmp_regions(tmpdirname)
        check_region_count(Dma)

        for tmp_region in TemporaryRegion.objects.iterator():
            name = tmp_region.name
            try:
                _LOGGER.info(f'Adding geometry to {name}')
                dma, dummy_created = Dma.objects.get_or_create(name=name)
                dma.geometry = tmp_region.geometry
                dma.save()
            except (Dma.DoesNotExist):
                _LOGGER.error(f'Skipping geometry for {name}')

    @staticmethod
    def _add_relations():
        """Relate DMAs to states."""
        for dma in Dma.objects.only('name').iterator():
            _LOGGER.info('Started processing DMA {dma}')

            for dma in Dma.objects.only('id').iterator():
                _LOGGER.info(f'Started processing DMA {dma}')
                states = State.objects.filter(
                    geometry__intersects=dma.geometry
                ).only('id')
                for state in states:
                    dma.states.add(state)
                    _LOGGER.info(f'Assigned DMA {dma} to {state}')

            try:
                dma_centroid = dma.geometry.centroid
                egrid = Egrid.objects.get(geometry__intersects=dma_centroid)
                dma.egrid = egrid
                dma.save()
                _LOGGER.info(f'Assigned {dma} to {dma}')
            except Egrid.DoesNotExist:
                _LOGGER.warning(f'No primary eGRID found for {dma}')

            _LOGGER.info('Finished processing DMA {dma}')

    @transaction.atomic  # rollback changes if anything goes wrong
    def handle(self, *args, **options):
        clear = options.get('clear', False)
        relate = options.get('relate', False)

        if clear:
            Dma.objects.all().delete()

        tmpdir = TemporaryDirectory()
        with tmpdir as tmpdirname:
            self._create_dmas(tmpdirname)

        if relate:
            self._add_relations()
