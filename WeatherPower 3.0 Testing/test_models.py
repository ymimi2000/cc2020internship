"""Tests Forecast models."""

from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
import pandas as pd

from forecasts.models import StateForecast
from testutils.factories import StateFactory
from wind.models import Turbine
from solar.models.solar_util import SolarUtility


class RegionForecastTest(TestCase):
    """Tests the RegionForecast model."""

    def setUp(self):
        self.forecast = StateForecast(
            region=StateFactory(),
            created=datetime(2019, 8, 1, 6, 0, 0),
            updated=datetime(2020, 1, 1, 6, 0, 0),
            solar_mwh=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            wind_mwh=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            solar_max=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            wind_max=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            solar_kwh_households=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            solar_tCO2_avoided=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            wind_tCO2_avoided=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        )

    def test_dates(self):
        """Test the dates property."""
        actual = self.forecast.dates
        expected = [
            datetime(2019, 12, 31, 6, 0, 0),
            datetime(2020, 1, 1, 6, 0),
            datetime(2020, 1, 2, 6, 0),
            datetime(2020, 1, 3, 6, 0),
            datetime(2020, 1, 4, 6, 0),
            datetime(2020, 1, 5, 6, 0),
        ]
        self.assertEqual(actual, expected)

    def test_days_of_week_current(self):
        """Test the days_of_week property for a current forecast."""
        after_update = datetime(2020, 1, 1, 23, 59, 0)
        with patch.object(timezone, 'now', return_value=after_update):
            actual = self.forecast.days_of_week
        expected = [
            'Yesterday',
            'Today',
            'Tomorrow',
            'Friday',
            'Saturday',
            'Sunday',
        ]
        self.assertEqual(actual, expected)

    def test_days_of_week_one_day_old(self):
        """Test the days_of_week property for a forecast from yesterday."""
        before_update = datetime(2020, 1, 2, 0, 0, 0)
        with patch.object(timezone, 'now', return_value=before_update):
            actual = self.forecast.days_of_week
        expected = [
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday',
        ]
        self.assertEqual(actual, expected)

    def test_is_current_true(self):
        """Test the is_current property for an up-to-date forecast."""
        with patch.object(
            timezone, 'now', return_value=datetime(2020, 1, 2, 6, 59, 0)
        ):
            self.assertTrue(self.forecast.is_current)

    def test_is_current_false(self):
        """Test the is_current property for an out-of-date forecast."""
        with patch.object(
            timezone, 'now', return_value=datetime(2020, 1, 2, 7, 0, 0)
        ):
            self.assertFalse(self.forecast.is_current)
