#!/usr/bin/env python
"""

"""
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand

from regions.models import County, Egrid, State

_SHAPEFILE = 'shapefiles/counties/tl_2017_us_county.shp'


class Command(BaseCommand):
    help = 'Load counties'

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
            'county_fips': 'COUNTYFP',
            'name': 'NAME',
            'name_lsad': 'NAMELSAD',
            'state_fips': 'STATEFP',
            'geometry': 'POLYGON',
        }
        lm = LayerMapping(County, shapefile, mapping)
        lm.save(verbose=True, strict=True)

    @staticmethod
    def _add_relations():
        """Relate counties to states."""

        for state in State.objects.only('fips').iterator():
            counties = County.objects.only('state_fips') \
                             .filter(state_fips=state.fips)
            counties.update(state=state)
            print('Assigned %s counties to %s' % (counties.count(), state))

        for county in County.objects.exclude(egrid__isnull=False):
            if not county.state.is_territory():
                try:
                    county_centroid = county.geometry.centroid
                    egrid = Egrid.objects.get(
                        geometry__intersects=county_centroid
                    )
                    county.egrid = egrid
                    county.save()
                    print('Assigned %s to %s' % (county, egrid))
                except Egrid.DoesNotExist:
                    print('Trying harder to find eGRID for %s %s...'
                          % (county, county.state))
                    try:
                        egrid = Egrid.objects.get(
                            geometry__intersects=county.geometry
                        )
                        county.egrid = egrid
                        county.save()
                        print('Assigned %s to %s' % (county, egrid))
                    except Egrid.DoesNotExist:
                        print('WARNING: No eGRID found for %s' % county)
                    except Egrid.MultipleObjectsReturned:
                        print('WARNING: Multiple eGRIDs found for %s' % county)

    def handle(self, *args, **options):
        self._add_geometries()
        self._add_relations()
