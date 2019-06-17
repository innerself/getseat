import datetime
from dataclasses import dataclass

from django.db import models
from django.db.models import ForeignKey


class Station(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)


class Train(models.Model):
    departure_station = ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='trains',
    )
    arrival_station = ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='trains',
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
        pass

    def _raw_page(self):
        date_format = '%d.%m.%Y'
        search_root = 'https://www.tutu.ru/poezda/rasp_d.php'
        dept_st = f'nnst1={self.departure_station.code}'
        arr_st = f'nnst2={self.arrival_station.code}'
        dt = f'date={self.date.strftime(date_format)}'
        search_url = f'{search_root}?{dept_st}&{arr_st}&{dt}'




    def _get_raw_schedule(self):




    def _parse_schedule(self):
        pass
