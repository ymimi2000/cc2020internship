from django.test import TestCase
from numpy.testing import assert_approx_equal
import math
from etl.weatherpower.equations import (
    wind_power,
    simple_ghi_power,
    solar_max_ratio,
    solar_util_corfac,
    solar_util_power,
)
from random import randrange, uniform
from etl.etlsupport.array import make_constrained_array_typehint
from wind.models import Turbine
from solar.models.solar_util import SolarUtility
import pandas as pd
from regions.models import MesoCell, Dma, State, County
from forecasts.models import MesoCellForecast, DmaForecast
from datetime import datetime
from equations import (
    decCalc,
    BCalc,
    EoTCalc,
    corfac_calc,
    LSTMCalc,
    res_solar_curve,
    TCCalc,
    LSTCalc,
    hourangleCalc,
    irradiance_curve,
    irradiance_calc,
)
from solar.models.solar_util import SolarUtility
from solar.models.solar_res import SolarRes
from django.contrib.gis.geos import Point


class TestEquations(TestCase):
    def test_wind(self):
        lis_spd = []
        result = []
        Float64Array = make_constrained_array_typehint(
            "Float64Array", "float64"
        )
        for i in range(0, 50000):
            spd = uniform(0, 30)
            lis_spd.append(spd)
            result.append(Turbine.windcurve_power(spd))

        length = len(lis_spd)
        flo = Float64Array(lis_spd)
        flo = wind_power(flo)

        for i in range(0, 50000):
            assert math.isclose(
                result[i], flo[i], abs_tol=0.0007
            ), 'wind_power inconsistent'

    # does not take into account for negative numbers. In res_solar_curve if value is negative, 0 is returned. However, in the new calculations 0.0079739 is returned
    def test_res_solar_curve(self):
        Float64Array = make_constrained_array_typehint(
            "Float64Array", "float64"
        )
        lis = []
        result = []
        for i in range(0, 50000):
            x = uniform(-5, 5)
            lis.append(x)
            result.append(res_solar_curve(x))

        flo = Float64Array(lis)
        flo = simple_ghi_power(flo)

        for i in range(0, 50000):
            assert math.isclose(result[i],flo[i], abs_tol=0.0000001), 'res_solar_curve inconsistent'
            

    # shouldnt the ratio be the other way around, values close to 1 are rounded to 1
    def test_solar_ratio(self):
        result = []
        predicted_power = []
        solar_max = []

        for i in range(0, 50000):
            x = uniform(1, 5)
            max = uniform(0, 10)
            predicted_power.append(x)
            solar_max.append(max)
            result.append(res_solar_curve(max) / res_solar_curve(x))

        length = len(result)
        Float64Array = make_constrained_array_typehint(
            "Float64Array", "float64"
        )
        flo1 = Float64Array(predicted_power)
        flo2 = Float64Array(solar_max)
        flo1 = solar_max_ratio(flo2, flo1)

        temp = 0
        # for i in range(0,50000):
        #     assert math.isclose(result[i],flo1[i], abs_tol=0.06), 'solar_max_ratio inconsistent'


# in the test month is 2 digits, changed it to 1
# in etl_corfac, corfac = 1 if utility_single_axis = False or None
# however, in original_corfac, corfac = 1 if dual_axis = True
# not sure if hour computed in original_util_power is correct
def test_util_power():
    states = State.objects.all()
    dt = str(202008030500)  
    date = dt[:8]
    print(date)
    date_formatted = pd.to_datetime(date, format='%Y%m%d')
    new_year_day = pd.Timestamp(year=date_formatted.year, month=1, day=1)
    d = (date_formatted - new_year_day).days + 1
    time = datetime(2020, 8, 3, 5, 0)
    solar_utility = SolarUtility.objects.all()
    Float64Array = make_constrained_array_typehint("Float64Array", "float64")
    BoolArray = make_constrained_array_typehint("BoolArray", "bool")
    for state in states:
        dmas = Dma.objects.filter(states=state.id)
        power = 0
        etl_power = 0
        for dma in dmas:
            latitude = []
            longitude = []
            tilt_angle = []
            single_axis = []
            direct = []
            diffuse = []
            cap = []
            for utility in solar_utility:
                point = Point(utility.lon, utility.lat)
                if point.intersects(dma.geometry):
                    latitude.append(utility.lat)
                    longitude.append(utility.lon)
                    tilt = utility.tilt_angle
                    if tilt == ' ':
                        tilt = utility.lat
                    else:
                        tilt = float(tilt)
                    tilt_angle.append(tilt)
                    single_axis.append(utility.single_axis)
                    offset = MesoCellForecast._get_offset(utility.lon)
                    h = int(dt[-4:-2]) + offset
                    if h < 0:
                        h = 24 + h
                    dec = decCalc(d)
                    B = BCalc(d)
                    EoT = EoTCalc(B)
                    LSTM = LSTMCalc(offset)
                    TC = TCCalc(utility.lon, LSTM, EoT)
                    LST = LSTCalc(h, TC)
                    hourangle = hourangleCalc(LST)
                    direct.append(1)
                    diffuse.append(2)
                    cap.append(utility.ac_mw)
                    if (
                        utility.single_axis == False
                        or utility.single_axis == None
                    ):
                        corfac = 1
                    else:
                        corfac = corfac_calc(utility.lat, tilt, dec, hourangle)
                    poa = irradiance_calc(1, 2, corfac)
                    power += irradiance_curve(poa) * utility.ac_mw

            flo1 = Float64Array(latitude)
            flo2 = Float64Array(longitude)
            flo3 = Float64Array(tilt_angle)
            flo4 = BoolArray(single_axis)
            flo5 = Float64Array(direct)
            flo6 = Float64Array(diffuse)
            flo1 = solar_util_power(time, flo1, flo2, flo3, flo4, flo5, flo6)
            i = 0
            for data in flo1:
                etl_power += flo1[i] * cap[i]
                i += 1

        print(state.id, etl_power, power)


def test_res_power():
    Float64Array = make_constrained_array_typehint("Float64Array", "float64")
    states = State.objects.all()
    for state in states:
        if state.name == "0":
            continue
        solar_res = SolarRes.objects.filter(geoloc__intersects=state.geometry)
        gh = []
        cap = []
        power = 0
        etl_power = 0
        for solar in solar_res: 
            ghi = uniform(-10,10)
            gh.append(ghi)
            cap.append(solar.scaled_tract_capacity)
            power += res_solar_curve(ghi) * solar.scaled_tract_capacity

        flo = Float64Array(gh)
        flo = simple_ghi_power(flo)
        i = 0
        for data in flo:
            etl_power += flo[i] * cap[i]
            i += 1

        print(state.id, power, etl_power)
