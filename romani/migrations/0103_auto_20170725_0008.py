# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-24 22:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('romani', '0102_auto_20170723_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='privat',
        ),
        migrations.RemoveField(
            model_name='producte',
            name='esgotat',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='punt_lat',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='punt_lng',
        ),
        migrations.AlterField(
            model_name='entrega',
            name='dia_entrega',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entregas', to='romani.DiaEntrega'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='invitacions',
            field=models.IntegerField(blank=True, default=4, null=True),
        ),
    ]