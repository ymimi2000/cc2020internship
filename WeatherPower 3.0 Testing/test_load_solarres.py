from io import StringIO
from django.core.management import call_command
from django.test import TestCase
import sys
from solar.models.solar_res import SolarRes


class LoadSolarResTestCase(TestCase):
    def test_command_output(self):
        out = StringIO()
        sys.stdout = out
        call_command('load_solarres', stdout=out)
        self.assertEqual(SolarRes.objects.count(), 162902)

        test_res = SolarRes.objects.filter(tract_id=50027966700.0)[0]
        self.assertEqual(test_res.Block_Group_Number, 4.0)
        self.assertEqual(test_res.Block_Group_LAT, 43.29072)
        self.assertEqual(test_res.Block_Group_LON, -72.452197)
        self.assertEqual(test_res.block_group_capacity, 1152.47039593025)
        self.assertEqual(test_res.source, 'TTS_2019')