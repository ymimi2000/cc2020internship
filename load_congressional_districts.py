#!/usr/bin/env python
"""

"""
import logging
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand

from regions.models import CongressionalDistrict, Egrid, State

_SHAPEFILE = 'shapefiles/congressional_districts/tl_2018_us_cd116.shp'
_LOGGER = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Load congressional districts'

    @staticmethod
    def _add_geometries():
        """Create records from a shapefile."""
        shapefile = os.path.join(settings.BASE_DIR, _SHAPEFILE)
        data_src = DataSource(shapefile)
        layer = data_src[0]
        print('Number of features:', len(layer))
        print('Geometry type:', layer.geom_type)
        print('Fields:', layer.fields)
        # for field in layer.fields:
        #     print(field, layer[0][field])
        print('Spatial Reference System:\n', layer.srs)

        mapping = {
            'id': 'GEOID',
            'name_lsad': 'NAMELSAD',
            'cd_fips': 'CD116FP',
            'state_fips': 'STATEFP',
            'cd_session': 'CDSESSN',
            'geometry': 'POLYGON',
        }
        lm = LayerMapping(CongressionalDistrict, shapefile, mapping)
        lm.save(verbose=True, strict=True)

    @staticmethod
    def _add_relations():
        """Relate states to congressional districts."""
        for cd in CongressionalDistrict.objects.iterator():
            cd.state = State.objects.only('id').get(fips=cd.state_fips)
            cd.save()

            if not cd.state.is_territory():
                try:
                    cd_centroid = cd.geometry.centroid
                    egrid = Egrid.objects.get(geometry__intersects=cd_centroid)
                    cd.egrid = egrid
                    cd.save()
                    print('Assigned %s to %s' % (cd, egrid))
                except Egrid.DoesNotExist:
                    print('Trying harder to find eGRID for %s...' % cd)
                    try:
                        egrid = Egrid.objects.get(
                            geometry__intersects=cd.geometry
                        )
                        cd.egrid = egrid
                        cd.save()
                        print('Assigned %s to %s' % (cd, egrid))
                    except Egrid.DoesNotExist:
                        print('WARNING: No eGRID found for %s' % cd)
                    except Egrid.MultipleObjectsReturned:
                        print('WARNING: Multiple eGRIDs found for %s' % cd)

    def handle(self, *args, **options):
        self._add_geometries()
        self._add_relations()
