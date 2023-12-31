# Generated by Django 3.2.15 on 2023-10-30 06:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('groupsapp', '0003_auto_20231030_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='week',
            name='trello_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='ID Trello'),
        ),
        migrations.AddField(
            model_name='week',
            name='trello_link',
            field=models.URLField(blank=True, verbose_name='Ссылка на Trello'),
        ),
        migrations.AlterField(
            model_name='week',
            name='end_date',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 10, 30, 6, 54, 12, 197439, tzinfo=utc), verbose_name='Дата окончания'),
        ),
    ]
