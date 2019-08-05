import datetime
import json

from django.core.management import BaseCommand

from getseat.models import TravelRouteParser, SeatsStatusSnapshot, TravelRoute


class Command(BaseCommand):
    help = 'Gets seat quantities from site and writes them to DB'

    def add_arguments(self, parser):
        parser.add_argument('date_window_days', nargs='+', type=int)

    def handle(self, *args, **options):
        routes_to_parse = TravelRoute.objects.all()

        for route_to_parse in routes_to_parse:
            date_window_days = options['date_window_days'][0]

            for time_offset in range(date_window_days):
                dt = datetime.date.today() + datetime.timedelta(
                    days=time_offset
                )

                parser = TravelRouteParser(
                    departure_station=route_to_parse.departure_station,
                    arrival_station=route_to_parse.arrival_station,
                    departure_date=dt,
                )

                schedule = parser.get_schedule()

                for train_card in schedule:
                    SeatsStatusSnapshot.objects.create(
                        train_number=train_card['train_number'],
                        departure_time=train_card['departure_time'],
                        seats=json.dumps(train_card['seats'], ensure_ascii=False),
                    )
