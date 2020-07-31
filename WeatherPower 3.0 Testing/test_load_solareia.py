from io import StringIO
from django.core.management import call_command
from django.test import TestCase
import sys
from solar.models.solar_util import SolarUtility

class LoadSolarEIATestCase(TestCase):
    def test_command_output(self):
        out = StringIO()
        sys.stdout = out
        call_command('load_solareia', stdout=out)
        self.assertEqual(SolarUtility.objects.count(), 3543)
        test_util = SolarUtility.objects.filter(plant_code=60695)[1]
        self.assertEqual(test_util.utilid, '60970')
        self.assertEqual(test_util.ac_mw, 1.0)
        self.assertEqual(test_util.dc_mw, '1.3')
        self.assertEqual(test_util.single_axis, False)
        self.assertEqual(test_util.dual_axis, None)
        self.assertEqual(test_util.fixed, True)
        self.assertEqual(test_util.east_west_fixed, False)
        self.assertEqual(test_util.tilt_angle, '25.0')
        self.assertEqual(test_util.lon, -93.857944)
        self.assertEqual(test_util.lat, 44.766167)
        self.assertEqual(test_util.zipcode, 55368)



