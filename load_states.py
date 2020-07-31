"""Create States from TIGER/Line and Cartographic Boundary shapefiles."""
import json
import logging
import os
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
import zipfile

from django.core.management.base import BaseCommand
from django.db import transaction

from regions.models import Egrid, State, TemporaryRegion

_YEAR = '2019'
_CB_SCALE = '20m'  # 1:20,000,000

# TIGER/Line (for spatial queries)
_TL_FILE = f'tl_{_YEAR}_us_state'
_TL_DOWNLOAD_URL = (
    f'https://www2.census.gov/geo/tiger/TIGER{_YEAR}/STATE/{_TL_FILE}.zip'
)

# Cartographic Boundaries (simplified geometry for web display)
_CB_FILE = f'cb_{_YEAR}_us_state_{_CB_SCALE}'
_CB_DOWNLOAD_URL = (
    f'https://www2.census.gov/geo/tiger/GENZ{_YEAR}/shp/{_CB_FILE}.zip'
)

_LOGGER = logging.getLogger('django')
_LOGGER.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Load states'

    def _download_shapefile(self, url, filename, tmpdirname):
        zip_file = os.path.join(tmpdirname, filename + '.zip')
        filehandle, _ = urlretrieve(url, filename=zip_file)
        with zipfile.ZipFile(filehandle, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)

    def _create_tmp_tl_regions(self, tmpdirname):
        """Create TemporaryRegions from a TIGER/Line shapefile."""
        self._download_shapefile(_TL_DOWNLOAD_URL, _TL_FILE, tmpdirname)
        shapefile = os.path.join(tmpdirname, _TL_FILE + '.shp')
        mapping = {
            'geoid': 'GEOID',
            'name': 'NAME',
            'abbrev': 'STUSPS',
            'internal_lat': 'INTPTLAT',
            'internal_lon': 'INTPTLON',
            'geometry': 'POLYGON',
        }
        TemporaryRegion.objects.create_from_shapefile(shapefile, mapping)

    def _create_tmp_cb_regions(self, tmpdirname):
        """Create TemporaryRegions from a Cartographic Boundaries shapefile."""
        self._download_shapefile(_CB_DOWNLOAD_URL, _CB_FILE, tmpdirname)
        shapefile = os.path.join(tmpdirname, _CB_FILE + '.shp')
        mapping = {
            'geoid': 'GEOID',
            'name': 'NAME',
            'abbrev': 'STUSPS',
            'geometry': 'POLYGON',
        }
        TemporaryRegion.objects.create_from_shapefile(shapefile, mapping)

    def _create_states(self, tmpdirname):
        """Create States from TemporaryRegions."""
        self._create_tmp_tl_regions(tmpdirname)
        for tmp_region in TemporaryRegion.objects.iterator():
            try:
                _LOGGER.info(f'Adding geometry to {tmp_region.name}')
                geoid = tmp_region.geoid
                state, dummy_created = State.objects.get_or_create(fips=geoid)
                state.coords = tmp_region.coords
                state.geometry = tmp_region.geometry
                state.name = tmp_region.name
                state.abbrev = tmp_region.abbrev
                state.save()
            except (State.DoesNotExist):
                _LOGGER.warning(f'Skipping geometry for {tmp_region.name}')

    def _add_geojson(self, tmpdirname):
        """Add geojson to States."""
        self._create_tmp_cb_regions(tmpdirname)
        for tmp_region in TemporaryRegion.objects.iterator():
            try:
                _LOGGER.info(f'Adding geojson to {tmp_region.name}')
                geoid = tmp_region.geoid
                state, dummy_created = State.objects.get_or_create(fips=geoid)
                state.geojson = json.loads(tmp_region.geometry.geojson)
                state.save()
            except (State.DoesNotExist):
                _LOGGER.warning(f'Skipping geojson for {tmp_region.name}')

    @staticmethod
    def _add_relations():
        """Relate states to eGRIDs."""
        for state in State.objects.only('id', 'coords').iterator():
            if not state.is_territory():
                try:
                    egrid = Egrid.objects.get(
                        geometry__intersects=state.coords
                    )
                    state.egrid = egrid
                    state.save()
                    _LOGGER.info('Assigned %s to %s' % (state, egrid))
                except Egrid.DoesNotExist:
                    _LOGGER.warning(f'No primary eGRID found for {state}')

    @transaction.atomic  # rollback changes if anything goes wrong
    def handle(self, *args, **options):
        tmpdir = TemporaryDirectory()
        with tmpdir as tmpdirname:
            self._create_states(tmpdirname)
            self._add_geojson(tmpdirname)
        self._add_relations()
