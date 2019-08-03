import datetime
import re

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


class Train(models.Model):
    number = models.CharField(max_length=10)
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
        self._date_format = '%d.%m.%Y'
        self._time_format = '%H:%M'
        self._site_root = 'https://www.tutu.ru'

    def get_schedule(self):
        # search_root = 'https://www.tutu.ru/poezda/rasp_d.php'
        dept_st = f'nnst1={self.departure_station.code}'
        arr_st = f'nnst2={self.arrival_station.code}'
        dt = f'date={self.date.strftime(self._date_format)}'
        search_url = f'{self._site_root}/poezda/rasp_d.php?{dept_st}&{arr_st}&{dt}'

        raw_schedule = self._get_raw_page(search_url)
        schedule = self._parse_schedule(raw_schedule)

        print()

    @staticmethod
    def _get_raw_page(url) -> str:
        with Browser() as browser:
            raw_page = browser.page_source(url)

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
            seats_element = card.find('span', {'seats_count'})
            seats_count = int(seats_element.text)

            seats_link = card.find(
                'a', {'top_bottom_prices_wrapper__link'}
            )['href']
            seats_url = f'{self._site_root}{seats_link}'

            seats_by_class = self._dispose_seats_by_class(seats_url)
            # TODO enter seats link and dispose seats by class
        except AttributeError:
            seats_count = None

        schedule_card_data = {
            'train_number': train_number,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'seats': {
                'count': seats_count,
            },
        }

        return schedule_card_data

    def _dispose_seats_by_class(self, url):
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

            seats_left = int(re.search('^(\\d+).*$', raw_seats_left).group(1))

            seats_by_class[seats_class] = seats_left

        return seats_by_class

    def _parse_time(self, time):
        return datetime.datetime.strptime(
            f'{self.date.day}.{str(self.date.month).zfill(2)}.{self.date.year}T{time}',
            f'{self._date_format}T{self._time_format}',
        )


class Browser:
    def __init__(self):
        self._exec_path = './geckodriver'
        self._options = self._set_options()
        self._profile = self._set_profile()
        self._inner_browser = None

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @staticmethod
    def _set_options():
        opt = Options()
        opt.headless = False

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

        self._inner_browser.start_client()
        print('Browser started')

    def stop(self):
        self._inner_browser.stop_client()

    def page_source(self, url):
        self._inner_browser.get(url)

        return self._inner_browser.page_source
