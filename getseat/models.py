import datetime

from bs4 import BeautifulSoup
from django.db import models
from django.db.models import ForeignKey
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver


class Station(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    departure_station = ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='departing_trains',
    )
    arrival_station = ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='arriving_trains',
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class TrainSearch:
    def __init__(self,
                 departure_station: Station,
                 arrival_station: Station,
                 date: datetime.date):

        self.departure_station = departure_station
        self.arrival_station = arrival_station
        self.date = date

    def get_schedule(self):
        raw_schedule = self._get_raw_page()
        schedule = self._parse_schedule(raw_schedule)

    def _get_raw_page(self) -> str:
        date_format = '%d.%m.%Y'
        search_root = 'https://www.tutu.ru/poezda/rasp_d.php'
        dept_st = f'nnst1={self.departure_station.code}'
        arr_st = f'nnst2={self.arrival_station.code}'
        dt = f'date={self.date.strftime(date_format)}'
        search_url = f'{search_root}?{dept_st}&{arr_st}&{dt}'

        browser = self._open_browser()
        browser.get(search_url)

        return browser.page_source

    def _parse_schedule(self, raw_schedule):
        soup = BeautifulSoup(raw_schedule, 'html.parser')
        schedule_cards = soup.find_all(
            'div', {'class': 'b-train__schedule__train_card'}
        )

        print()

    @staticmethod
    def _open_browser() -> WebDriver:

        opt = Options()
        # opt.headless = True

        profile = FirefoxProfile()
        profile.set_preference("permissions.default.image", 2)

        browser = Firefox(
            executable_path='./geckodriver',
            options=opt,
            firefox_profile=profile,
        )

        return browser



