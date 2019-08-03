import datetime

from django.test import TestCase
from selenium.webdriver.firefox.webdriver import WebDriver

from getseat.models import Station, Train, TrainSearch


class TrainSearchTests(TestCase):

    def setUp(self) -> None:
        Station.objects.create(
            name='Москва',
            code='2000000',
        )

        Station.objects.create(
            name='Тарусская',
            code='2001062',
        )

    def tearDown(self) -> None:
        pass

    def test_get_raw_page(self):
        search = TrainSearch(
            departure_station=Station(name='Москва', code='2000000'),
            arrival_station=Station(name='Тарусская', code='2001062'),
            date=datetime.date(2019, 7, 12),
        )

        self.assertTrue('j-content s-disabled' in search._get_raw_page())

        search = TrainSearch(
            departure_station=Station(name='Москва', code='9999999'),
            arrival_station=Station(name='Тарусская', code='1234567'),
            date=datetime.date(2019, 7, 12),
        )

        self.assertTrue('j-content s-disabled' not in search._get_raw_page())

    def test_open_browser(self):
        self.assertIsInstance(TrainSearch._start_browser(), WebDriver)

    def test_parse_schedule(self):
        search = TrainSearch(
            departure_station=Station.objects.get(pk=1),
            arrival_station=Station.objects.get(pk=2),
            date=datetime.date(2019, 8, 1),
        )

        # raw_page = search._get_raw_page()
        # schedule = search._parse_schedule(raw_schedule=raw_page)
        schedule = search.get_schedule()

