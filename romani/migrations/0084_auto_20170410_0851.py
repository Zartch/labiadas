# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-10 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('romani', '0083_auto_20170410_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producte',
            name='karma_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
