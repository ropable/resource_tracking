# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-04 02:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0027_remove_device_usual_callsign'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='current_callsign',
            new_name='callsign',
        ),
    ]