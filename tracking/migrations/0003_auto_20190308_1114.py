# Generated by Django 2.0.9 on 2019-03-08 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_auto_20190111_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='district',
            field=models.CharField(choices=[('SWAN', 'Swan Region'), ('PHD', 'Perth Hills'), ('SCD', 'Swan Coastal'), ('SWR', 'South West Region'), ('BWD', 'Blackwood'), ('WTN', 'Wellington'), ('WR', 'Warren Region'), ('DON', 'Donnelly'), ('FRK', 'Frankland'), ('SCR', 'South Coast Region'), ('ALB', 'Albany'), ('ESP', 'Esperance'), ('KIMB', 'Kimberley Region'), ('EKD', 'East Kimberley'), ('WKD', 'West Kimberley'), ('PIL', 'Pilbara Region'), ('EXM', 'Exmouth'), ('GLD', 'Goldfields Region'), ('MWR', 'Midwest Region'), ('GER', 'Geraldton'), ('KLB', 'Kalbarri'), ('MOR', 'Moora'), ('SHB', 'Shark Bay'), ('WBR', 'Wheatbelt Region'), ('CWB', 'Central Wheatbelt'), ('SWB', 'Southern Wheatbelt'), ('AV', 'Aviation'), ('OTH', 'Other')], default='OTH', max_length=32, verbose_name='Region/District'),
        ),
    ]
