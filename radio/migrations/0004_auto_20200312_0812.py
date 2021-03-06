# Generated by Django 2.2.11 on 2020-03-12 00:12

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0003_auto_20200306_0727'),
    ]

    operations = [
        migrations.RenameField(
            model_name='networkrxanalysis',
            old_name='last_downloaded',
            new_name='process_end',
        ),
        migrations.RenameField(
            model_name='networktxanalysis',
            old_name='last_downloaded',
            new_name='process_end',
        ),
        migrations.RenameField(
            model_name='repeaterrxanalysis',
            old_name='last_downloaded',
            new_name='process_end',
        ),
        migrations.RenameField(
            model_name='repeatertxanalysis',
            old_name='last_downloaded',
            new_name='process_end',
        ),
        migrations.RemoveField(
            model_name='repeaterrxanalysis',
            name='geom',
        ),
        migrations.RemoveField(
            model_name='repeatertxanalysis',
            name='geom',
        ),
        migrations.AddField(
            model_name='networkrxanalysis',
            name='process_msg',
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='networkrxanalysis',
            name='process_start',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='networkrxanalysis',
            name='process_status',
            field=models.SmallIntegerField(choices=[(0, 'Idle'), (110, 'Waiting to process'), (-122, 'Delete Failed'), (120, 'Waiting to delete'), (121, 'Deleting Calculation'), (129, 'Deleted Calculation'), (-132, 'Analyse Failed'), (130, 'Waiting to analyse'), (131, 'Analysing'), (139, 'Analysed'), (-142, 'Download Failed'), (140, 'Waiting to download'), (141, 'Downloading'), (149, 'Downloaded'), (-152, 'Extracting Failed'), (150, 'Waiting to extract'), (151, 'Extrating Spatial Data'), (-9998, 'Timeout'), (-9999, 'Failed')], default=0, editable=False),
        ),
        migrations.AddField(
            model_name='networktxanalysis',
            name='process_msg',
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='networktxanalysis',
            name='process_start',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='networktxanalysis',
            name='process_status',
            field=models.SmallIntegerField(choices=[(0, 'Idle'), (110, 'Waiting to process'), (-122, 'Delete Failed'), (120, 'Waiting to delete'), (121, 'Deleting Calculation'), (129, 'Deleted Calculation'), (-132, 'Analyse Failed'), (130, 'Waiting to analyse'), (131, 'Analysing'), (139, 'Analysed'), (-142, 'Download Failed'), (140, 'Waiting to download'), (141, 'Downloading'), (149, 'Downloaded'), (-152, 'Extracting Failed'), (150, 'Waiting to extract'), (151, 'Extrating Spatial Data'), (-9998, 'Timeout'), (-9999, 'Failed')], default=0, editable=False),
        ),
        migrations.AddField(
            model_name='repeater',
            name='rx_antenna_gain',
            field=models.FloatField(blank=True, null=True, verbose_name='RX Transmitter antenna  gain in dBi'),
        ),
        migrations.AddField(
            model_name='repeater',
            name='rx_power',
            field=models.FloatField(blank=True, null=True, verbose_name='RX Transmitter RF power in Watts,20dBm=0.1w'),
        ),
        migrations.AddField(
            model_name='repeater',
            name='tx_antenna_gain',
            field=models.FloatField(blank=True, null=True, verbose_name='TX Transmitter antenna  gain in dBi'),
        ),
        migrations.AddField(
            model_name='repeater',
            name='tx_power',
            field=models.FloatField(blank=True, null=True, verbose_name='TX Transmitter RF power in Watts,20dBm=0.1w'),
        ),
        migrations.AddField(
            model_name='repeaterrxanalysis',
            name='process_msg',
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='repeaterrxanalysis',
            name='process_start',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='repeaterrxanalysis',
            name='process_status',
            field=models.SmallIntegerField(choices=[(0, 'Idle'), (110, 'Waiting to process'), (-122, 'Delete Failed'), (120, 'Waiting to delete'), (121, 'Deleting Calculation'), (129, 'Deleted Calculation'), (-132, 'Analyse Failed'), (130, 'Waiting to analyse'), (131, 'Analysing'), (139, 'Analysed'), (-142, 'Download Failed'), (140, 'Waiting to download'), (141, 'Downloading'), (149, 'Downloaded'), (-152, 'Extracting Failed'), (150, 'Waiting to extract'), (151, 'Extrating Spatial Data'), (-9998, 'Timeout'), (-9999, 'Failed')], default=0, editable=False),
        ),
        migrations.AddField(
            model_name='repeatertxanalysis',
            name='process_msg',
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='repeatertxanalysis',
            name='process_start',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='repeatertxanalysis',
            name='process_status',
            field=models.SmallIntegerField(choices=[(0, 'Idle'), (110, 'Waiting to process'), (-122, 'Delete Failed'), (120, 'Waiting to delete'), (121, 'Deleting Calculation'), (129, 'Deleted Calculation'), (-132, 'Analyse Failed'), (130, 'Waiting to analyse'), (131, 'Analysing'), (139, 'Analysed'), (-142, 'Download Failed'), (140, 'Waiting to download'), (141, 'Downloading'), (149, 'Downloaded'), (-152, 'Extracting Failed'), (150, 'Waiting to extract'), (151, 'Extrating Spatial Data'), (-9998, 'Timeout'), (-9999, 'Failed')], default=0, editable=False),
        ),
        migrations.CreateModel(
            name='RepeaterTXCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=128)),
                ('district', models.CharField(editable=False, max_length=64)),
                ('dn', models.IntegerField(editable=False, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(editable=False, null=True, srid=4326)),
                ('repeater', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='radio.Repeater')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RepeaterRXCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=128)),
                ('district', models.CharField(editable=False, max_length=64)),
                ('dn', models.IntegerField(editable=False, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(editable=False, null=True, srid=4326)),
                ('repeater', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='radio.Repeater')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
