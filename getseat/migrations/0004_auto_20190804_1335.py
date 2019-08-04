# Generated by Django 2.2.4 on 2019-08-04 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('getseat', '0003_seatsstatussnapshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='TravelRoute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure_date', models.DateField()),
                ('arrival_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travels_ending_here', to='getseat.Station')),
                ('departure_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travels_starting_here', to='getseat.Station')),
            ],
        ),
        migrations.DeleteModel(
            name='Train',
        ),
    ]
