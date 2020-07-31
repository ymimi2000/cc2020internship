from django.test import TestCase

from forecasts.utils import (
    get_day_slice,
    split_six_day_forecast,
    new_float_array,
    new_int_array,
    format_num,
)


class ForecastUtilsTest(TestCase):
    """Tests the RegionForecast model."""

    def setUp(self):
        self.day_0 = [0] * 24
        self.day_1 = [2] * 24
        self.day_2 = [4] * 24
        self.day_3 = [6] * 24
        self.day_4 = [8] * 24
        self.day_5 = [10] * 12
        self.forecast = (
            self.day_0
            + self.day_1
            + self.day_2
            + self.day_3
            + self.day_4
            + self.day_5
        )

    def test_get_day_slice(self):
        """Test the get_day_slice function."""
        self.assertEqual(get_day_slice(self.forecast, 0), self.day_0)
        self.assertEqual(get_day_slice(self.forecast, 5), self.day_5)

    def test_split_six_day_forecast(self):
        """Test the split_six_day_forecast function."""
        actual = split_six_day_forecast(self.forecast)
        expected = [
            self.day_0,
            self.day_1,
            self.day_2,
            self.day_3,
            self.day_4,
            self.day_5 + [0] * 12,
        ]
        self.assertEqual(actual, expected)

    def test_new_float_array(self):
        """Test the new_float_array function."""
        actual = new_float_array()
        expected = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.assertEqual(actual, expected)
        self.assertTrue(isinstance(expected[0], float))

    def test_new_int_array(self):
        """Test the new_int_array function."""
        actual = new_int_array()
        expected = [0, 0, 0, 0, 0, 0]
        self.assertEqual(actual, expected)
        self.assertTrue(isinstance(expected[0], int))

    def test_format_num(self):
        """Test the format_num function."""
        self.assertEqual(format_num(0), 0)
        self.assertEqual(format_num(0.000), 0)
        self.assertEqual(format_num(0.955), 1)
        self.assertEqual(format_num(1.9), 2)
        self.assertEqual(format_num(1.99), 2)
