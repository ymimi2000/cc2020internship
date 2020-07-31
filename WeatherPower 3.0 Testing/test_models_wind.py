"""
test_models.py: Test turbine model calculations and turbine power
calculations.

Turbine model: AAER A1500-70, with 80m hub height
https://en.wind-turbine-models.com/turbines/597-aaer-a1500-70

Uses a forecast of constant wind speed to avoid reading from S3.
"""
from django.test import TestCase

from testutils.factories import MesoFactory
from wind.models import TurbineModel, TurbineManufacturer, Turbine


class WindTestCase(TestCase):

    def setUp(self):
        cell = MesoFactory()
        manufacturer = TurbineManufacturer.objects.create(name='AAER')
        self.model_with_cap = TurbineModel.objects.create(
            model_id='A-1500',
            manufacturer=manufacturer,
            capacity=1500.0,
            hub_height=80.0,
            rotor_diameter=77.0
        )
        self.model_no_cap = TurbineModel.objects.create(
            model_id='0000',
            manufacturer=manufacturer,
            capacity=None,
            hub_height=80.0,
            rotor_diameter=77.0
        )
        self.turbine_with_cap = Turbine.objects.create(
            id='123',
            model=self.model_with_cap,
            meso_cell=cell,
            county=cell.county,
            state=cell.state,
            coordinates=cell.centroid
        )
        self.turbine_no_cap = Turbine.objects.create(
            id='no_cap',
            model=self.model_no_cap,
            meso_cell=cell,
            county=cell.county,
            state=cell.state,
            coordinates=cell.centroid
        )
        self.power_array = [3.0] * 132


class TurbineModelTestCase(WindTestCase):

    def test_rotor_swept_area(self):
        self.assertEqual(self.model_with_cap.rotor_swept_area, 4657)

    def test_total_height(self):
        self.assertEqual(self.model_with_cap.total_height, 118.5)


class TurbineTestCase(WindTestCase):

    def test_turbine_power_with_capacity(self):
        """Test power for a turbine with capacity data."""
        turbine = self.turbine_with_cap
        capacity = turbine.model.capacity
        actual = [round(x, 5) for x in turbine.turbine_power(self.power_array)]
        vals = [round(0.007650668733535544 * 24 * capacity, 5)] * 5
        vals += [round(0.007650668733535544 * 12 * capacity, 5)]
        expected = vals
        self.assertEqual(actual, expected)

    def test_turbine_power_no_capacity(self):
        """Test power for a turbine without capacity data."""
        turbine = self.turbine_no_cap
        actual = [round(x, 5) for x in turbine.turbine_power(self.power_array)]
        vals = [0] * 6
        expected = vals
        self.assertEqual(actual, expected)

    def test_windcurve_power(self):
        turbine = self.turbine_with_cap
        self.assertEqual(round(turbine.windcurve_power(3.0), 9), 0.007650669)
        self.assertEqual(round(turbine.windcurve_power(14.0), 4), 0.9646)
        self.assertEqual(round(turbine.windcurve_power(23.0), 7), 0.3858586)
        self.assertEqual(turbine.windcurve_power(28.0), 0)
