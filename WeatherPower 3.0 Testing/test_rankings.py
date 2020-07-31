# test rankings
from django.test import TestCase
from forecasts.models import (
    StateForecast,
    DmaForecast,
    CountyForecast,
    CongressionalDistrictForecast,
)
from regions.models import MesoCell, State, Dma, CongressionalDistrict, County
from forecasts.rankings import (
    solarAbsoluteRankings,
    wind_absolute_rankings,
    solar_per_capita,
    wind_per_capita,
)
from random import randrange
from numpy.testing import assert_approx_equal

population = []  # stores population for each region
solar_mwh = []  # stores solar_mwh for each region


class TestRankings(TestCase):
    global population
    global solar_mwh

    def setUp(self):

        a = randrange(40, 60)
        global population
        lat = 0.5

        for i in range(0, a):
            solar_mwh.append([i, i + 1, i + 2, i + 3, i + 4, i + 5])

            state = State.objects.create(id=str(i), name=str(i))

            county = County.objects.create(
                id=str(i), name=str(i), name_lsad=str(i)
            )

            dma = Dma.objects.create(name=str(i), display_name=str(i))

            cd = CongressionalDistrict.objects.create(
                id=str(i), state=state, cd_fips=str(i)
            )

            StateForecast.objects.create(
                region=state,
                solar_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_kwh_households=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
            )

            CountyForecast.objects.create(
                region=county,
                solar_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_kwh_households=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
            )

            DmaForecast.objects.create(
                region=dma,
                solar_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_kwh_households=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
            )

            CongressionalDistrictForecast.objects.create(
                region=cd,
                solar_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_mwh=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_kwh_households=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                solar_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
                wind_tCO2_avoided=[i, i + 1, i + 2, i + 3, i + 4, i + 5],
            )
            pop = 0
            b = randrange(100, 500)
            # create mesocells associated with the regions
            for j in range(0, b):
                x = randrange(500, 10000)
                MesoCell.objects.create(
                    latitude=lat,
                    longitude=lat,
                    state=state,
                    county=county,
                    dma=dma,
                    congressional_district=cd,
                    population=x,
                )
                lat = lat + 1
                pop = pop + x

            population.append(pop)

    def test_absolute_rankings(self):
        global solar_mwh
        global population
        regions = ['state', 'county', 'dma', 'congressionaldistrict']
        for reg in regions:
            query = {'region_type': reg, 'forecast_days': [0, 1, 2, 3, 4, 5]}
            dict_solar = solarAbsoluteRankings(query)
            dict_wind = wind_absolute_rankings(query)
            for i in range(0, 6):
                value_solar = dict_solar[i][0]['solar_mwh__{}'.format(i)]
                value_wind = dict_wind[i][0]['wind_mwh__{}'.format(i)]
                length = len(population)
                for j in range(1, length):
                    x = dict_solar[i][j]['solar_mwh__{}'.format(i)]
                    y = dict_wind[i][j]['wind_mwh__{}'.format(i)]
                    if x > value_solar:
                        raise ValueError('Rankings are not in correct order')
                    if y > value_wind:
                        raise ValueError('Rankings are not in correct order')
                    value_solar = x
                    value_wind = y
        solar_mwh = []
        population = []

    def test_per_capita_rankings(self):
        global population
        global solar_mwh
        regions = ['state', 'county', 'dma', 'congressionaldistrict']
        for reg in regions:
            query = {'region_type': reg, 'forecast_days': [0, 1, 2, 3, 4, 5]}
            dict_solar = solar_per_capita(query)
            dict_wind = wind_per_capita(query)
            length = len(population)

            for i in range(0, 6):
                lookup_s = int(dict_solar[i][0][1])
                lookup_w = int(dict_wind[i][0][1])
                value_solar = dict_solar[i][0][0]
                assert_approx_equal(
                    value_solar,
                    (solar_mwh[lookup_s][i] / population[lookup_s]),
                    err_msg='solar_mwh / population is incorrect',
                )

                value_wind = dict_wind[i][0][0]
                assert_approx_equal(
                    value_wind,
                    (solar_mwh[lookup_w][i] / population[lookup_w]),
                    err_msg='wind_mwh / population is incorrect',
                )

                for j in range(1, length):
                    lookup_s = int(dict_solar[i][j][1])
                    lookup_w = int(dict_wind[i][j][1])
                    x = dict_solar[i][j][0]
                    y = dict_wind[i][j][0]
                    if x > value_solar:
                        raise ValueError(
                            'Solar per capita Rankings'
                            'are not in correct order'
                        )
                    assert_approx_equal(
                        x,
                        (solar_mwh[lookup_s][i] / population[lookup_s]),
                        err_msg='solar_mwh / population is incorrect',
                    )
                    if y > value_wind:
                        raise ValueError(
                            'Wind per capita Rankings are not in correct order'
                        )

                    assert_approx_equal(
                        y,
                        (solar_mwh[lookup_w][i] / population[lookup_w]),
                        err_msg='wind_mwh / population is incorrect',
                    )

                    value_solar = x
                    value_wind = y
