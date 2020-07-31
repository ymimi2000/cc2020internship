from io import StringIO
from django.core.management import call_command
from django.test import TestCase
import sys
from regions.models import State


class LoadStateSEIATestCase(TestCase):
    def test_command_output(self):
        out = StringIO()
        sys.stdout = out
        call_command('load_stateSEIA', stdout=out)
        self.assertEqual(State.objects.count(), 56)
        test_state = State.objects.get(name="California")
        self.assertEqual(test_state.fips, '06')
        self.assertEqual(test_state.num_of_consumers, 13591152)
        self.assertEqual(test_state.avg_monthly_consumption_kwh, 546.0)
        self.assertEqual(test_state.avg_price_cents_per_kwh, 18.84)
        self.assertEqual(test_state.avg_monthly_bill_dollars, 102.9)
        self.assertEqual(test_state.co2_emissions_factor, 0.216)
        self.assertEqual(test_state.seia_mw, 27897.04)