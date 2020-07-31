import updatedb as ub

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Calling dailyForecast...')
        ub.update_forecast()
        print('Finished calling dailyForecast.')
