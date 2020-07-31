#!/usr/bin/env python
"""

"""
import json
import logging
import os

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from regions.models import County, MesoCell, State
from wind.models import Turbine, TurbineManufacturer, TurbineModel
from windsolarsite.utils import update_fields

_LOGGER = logging.getLogger('django')
_GEO_FILE = os.path.join(settings.BASE_DIR,
                         'geojson/uswtdbGeoJSON/uswtdb_v3_0_1_20200514.geojson')


class Command(BaseCommand):
    help = 'Load turbines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='delete existing turbines before loading data'
        )

    @staticmethod
    def _get_turbine_manufacturer(props):
        """Get or create a TurbineManufacturer from a turbine's properties."""
        t_manu = props['t_manu'] or 'Unknown'
        (manufacturer, created) = TurbineManufacturer.objects.get_or_create(
            name=t_manu,
        )
        if created:
            print('Saved turbine manufacturer', manufacturer)
        return manufacturer

    @staticmethod
    def _get_model_id(props):
        """Get or create a model ID from a turbine's properties.

        If the model is unknown, create an ID using the turbine's specs.
        """
        t_cap = props['t_cap'] or '?'
        t_hh = props['t_hh'] or '?'
        t_rd = props['t_rd'] or '?'
        default_model_id = 'Unknown Model %s/%s/%s' % (t_cap, t_hh, t_rd)
        return props['t_model'] or default_model_id

    def _get_turbine_model(self, props):
        """Create or update a TurbineModel from a turbine's properties."""
        manufacturer = self._get_turbine_manufacturer(props)
        model_id = self._get_model_id(props)
        (turbine_model, created) = TurbineModel.objects.get_or_create(
            manufacturer=manufacturer,
            model_id=model_id,
        )

        mapping = {
            'capacity': 't_cap',
            'hub_height': 't_hh',
            'rotor_diameter': 't_rd',
        }

        did_update = update_fields(turbine_model, props, mapping)

        if created or did_update:
            turbine_model.save()
            print('Saved turbine model', turbine_model)

        return turbine_model

    def _create_turbine(self, feature):
        """Create or update a Turbine associated with a point feature."""
        props = feature['properties']
        (turbine, created) = Turbine.objects.get_or_create(id=props['case_id'])
        if created or not turbine.meso_cell:
            turbine.model = self._get_turbine_model(props)
            turbine.coordinates = GEOSGeometry(json.dumps(feature['geometry']))
            turbine.state = State.objects.get(id=props['t_state'])
            try:
                turbine.county = County.objects.get(
                    geometry__intersects=turbine.coordinates
                )
            except County.DoesNotExist:
                _LOGGER.warning('No county found for turbine %s', turbine)
            try:
                turbine.meso_cell = MesoCell.objects.get(
                    geometry__intersects=turbine.coordinates
                )
            except MesoCell.DoesNotExist:
                _LOGGER.warning('No MesoCell found for turbine %s', turbine)
            except MesoCell.MultipleObjectsReturned:
                mesocells = MesoCell.objects.filter(
                    geometry__intersects=turbine.coordinates
                )
                turbine.meso_cell = mesocells.first()
                _LOGGER.warning('Multiple MesoCells (%s) found for turbine %s',
                                mesocells, turbine)
            turbine.save()
            print('Saved turbine', turbine)
        else:
            print('Skipping turbine', turbine)

    def _create_turbines(self):
        """Load turbine data from the geojson file."""
        try:
            with open(_GEO_FILE) as file:
                geojson = json.load(file)
                features = geojson['features']
                print('Loading %s turbines' % len(features))
                for feature in features:
                    self._create_turbine(feature)
        except FileNotFoundError as error:
            _LOGGER.error(error)

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options.get('clear', False)
        if clear:
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE turbine')
            print('Cleared turbine table')
        self._create_turbines()
