import datetime
import re
import time

from pathlib import Path
from django.conf import settings

from bs4 import BeautifulSoup
from django.db import models
from django.db.models import ForeignKey
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options


class Station(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name


class TravelRoute(models.Model):
    departure_date = models.DateField()
    departure_station = ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='travels_starting_here',
    )
    arrival_station = ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='travels_ending_here',
    )


class SeatsStatusSnapshot(models.Model):
    snapshot_time = models.DateTimeField(auto_now_add=True)
    train_number = models.CharField(max_length=64)
    departure_time = models.DateTimeField()
    seats = models.CharField(max_length=255)


class TravelRouteParser:
    def __init__(self,
                 departure_station: Station,
                 arrival_station: Station,
                 departure_date: datetime.date):

        self.departure_station = departure_station
        self.arrival_station = arrival_station
        self.departure_date = departure_date
        self._date_format = '%d.%m.%Y'
        self._time_format = '%H:%M'
        self._site_root = 'https://www.tutu.ru'

    def get_schedule(self):
        dept_st = f'nnst1={self.departure_station.code}'
        arr_st = f'nnst2={self.arrival_station.code}'
        dt = f'date={self.departure_date.strftime(self._date_format)}'
        search_url = f'{self._site_root}/poezda/rasp_d.php?{dept_st}&{arr_st}&{dt}'

        raw_schedule = self._get_raw_page(search_url)
        schedule = self._parse_schedule(raw_schedule)

        return schedule

    @staticmethod
    def _get_raw_page(url: str) -> str:
        wait_time = 2
        captcha_string = 'Введите цифры с картинки'

        while True:
            with Browser() as browser:
                raw_page = browser.page_source(url)

            if captcha_string in raw_page:
                time.sleep(wait_time)
                wait_time *= 2
            else:
                break

        return raw_page

    @staticmethod
    def _get_page_soup(page):
        return BeautifulSoup(page, 'html.parser')

    def _parse_schedule(self, raw_schedule):
        soup = self._get_page_soup(raw_schedule)
        schedule_cards = soup.find_all(
            'div', {'class': 'b-train__schedule__train_card'}
        )

        schedule = [
            self._parse_schedule_card(schedule_card)
            for schedule_card
            in schedule_cards
        ]

        return schedule

    def _parse_schedule_card(self, card) -> dict:
        train_number = card.find(
            'span', {'train_number_link'}
        ).find('span').text

        departure_time = self._parse_time(
            card.find('div', {'departure_time'}).text
        )

        arrival_time = self._parse_time(
            card.find('span', {'schedule_time'}).text
        )

        try:
            seats_link = card.find(
                'a', {'top_bottom_prices_wrapper__link'}
            )['href']
            seats_url = f'{self._site_root}{seats_link}'

            seats = self._dispose_seats_by_class(seats_url)
        except (AttributeError, TypeError):
            seats = None

        schedule_card_data = {
            'train_number': train_number,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'seats': seats,
        }

        return schedule_card_data

    def _dispose_seats_by_class(self, url: str) -> dict:
        raw_page = self._get_raw_page(url)
        soup = self._get_page_soup(raw_page)

        seat_cards = soup.find_all('div', {'category_select_row_wrp'})

        seats_by_class = {}
        for card in seat_cards:
            seats_class = card.find(
                'span', {'data-ti': 'srv_class'}
            ).findChild().text.strip()[1:-1]

            raw_seats_left = card.find(
                'div', {'data-ti': 'category_select_seats_all'}
            ).findChild().text

            seats_left = int(re.search(r'^(\d+).*$', raw_seats_left).group(1))

            seats_by_class[seats_class] = seats_left

        return seats_by_class

    def _parse_time(self, time: str) -> datetime:
        return datetime.datetime.strptime(
            f'{self.departure_date.day}.{str(self.departure_date.month).zfill(2)}.{self.departure_date.year}T{time}',
            f'{self._date_format}T{self._time_format}',
        )


class Browser:
    def __init__(self):
        self._exec_path = Path(
            settings.BASE_DIR
        ).joinpath('geckodriver').as_posix()

        self._options = self._set_options()
        self._profile = self._set_profile()
        self._inner_browser = None

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @staticmethod
    def _set_options():
        opt = Options()
        opt.headless = True

        return opt

    @staticmethod
    def _set_profile():
        profile = FirefoxProfile()
        profile.set_preference("permissions.default.image", 2)

        return profile

    def start(self):
        self._inner_browser = Firefox(
            executable_path=self._exec_path,
            options=self._options,
            firefox_profile=self._profile,
        )

    def stop(self):
        self._inner_browser.close()

    def page_source(self, url):
        self._inner_browser.get(url)

        return self._inner_browser.page_source
