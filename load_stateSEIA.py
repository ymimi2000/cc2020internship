#!/usr/bin/env python
"""

"""
import csv
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from regions.models import State

_LOGGER = logging.getLogger('django')


def _convert_to_bool(val):
    """Convert a 'Y' value to True and an 'N' to False."""
    vals = {
        'Y': True,
        'N': False,
    }
    return vals.get(val)


class Command(BaseCommand):
    help = 'Load state SEIA data'

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'solar/SEIAdata.csv')
        with open(path, 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                state_seia = State.objects.get(name=str(row[0]))
                state_seia.seia_dc_mw = float(row[1])
                state_seia.save()

        # From https://www.eia.gov/electricity/sales_revenue_price/ Table 5a
        path = os.path.join(settings.BASE_DIR, 'solar/statedata.csv')
        with open(path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                state_data = State.objects.get(name=str(row[0]))
                state_data.num_of_consumers = int(row[1])
                state_data.avg_monthly_consumption_kwh = float(row[2])
                state_data.avg_price_cents_per_kwh = float(row[3])
                state_data.avg_monthly_bill_dollars = float(row[4])
                state_data.save()
