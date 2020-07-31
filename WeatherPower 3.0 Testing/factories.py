import factory
from django.contrib.gis.geos import Point

from regions.models import (
    CongressionalDistrict,
    County,
    Dma,
    Egrid,
    MesoCell,
    State,
    Zcta,
    Timezone
)

from forecasts.utils import new_float_array
from forecasts.models.mesocell_forecast import MesoCellForecast


class CdFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CongressionalDistrict


class CountyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = County


class EgridFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Egrid


class DmaFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Dma

    egrid = factory.SubFactory(EgridFactory)


class StateFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = State

    egrid = factory.SubFactory(EgridFactory)


class ZctaFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Zcta


class TimezoneFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Timezone


class MesoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = MesoCell

    county = factory.SubFactory(CountyFactory)
    zcta = factory.SubFactory(ZctaFactory)
    egrid = factory.SubFactory(EgridFactory)
    dma = factory.SubFactory(DmaFactory, egrid=None)
    state = factory.SubFactory(StateFactory, egrid=None)
    congressional_district = factory.SubFactory(CdFactory)
    timezone = factory.SubFactory(TimezoneFactory)
    area = 100
    population = 1000
    res_cap = 5.5
    latitude = 90.5
    longitude = 34.0
    centroid = Point(latitude, longitude)
    geometry = None


class MesoCellForecastFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = MesoCellForecast

    region = factory.SubFactory(MesoFactory)
    solar_mwh = new_float_array()
    wind_mwh = new_float_array()
    solar_max = 0
    wind_max = 0
    solar_kwh_households = new_float_array()
    solar_tCO2_avoided = new_float_array()
    wind_tCO2_avoided = new_float_array()
