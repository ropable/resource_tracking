# Generated by Django 4.2.11 on 2024-04-24 07:32

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracking", "0021_auto_20231020_1146"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceView",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("point", django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ("heading", models.IntegerField()),
                ("velocity", models.IntegerField()),
                ("altitude", models.IntegerField()),
                ("seen", models.DateTimeField()),
                ("deviceid", models.CharField(max_length=32)),
                ("registration", models.CharField(max_length=32)),
                ("rin_display", models.CharField(max_length=5)),
                ("current_driver", models.CharField(max_length=50)),
                ("callsign", models.CharField(max_length=50)),
                ("callsign_display", models.CharField(max_length=50)),
                ("usual_driver", models.CharField(max_length=50)),
                ("usual_location", models.CharField(max_length=50)),
                ("contractor_details", models.CharField(max_length=50)),
                (
                    "symbol",
                    models.CharField(
                        choices=[
                            ("2 wheel drive", "2-Wheel Drive"),
                            ("4 wheel drive passenger", "4-Wheel Drive Passenger"),
                            ("4 wheel drive ute", "4-Wheel Drive (Ute)"),
                            ("light unit", "Light Unit"),
                            ("heavy duty", "Heavy Duty"),
                            ("gang truck", "Gang Truck"),
                            ("snorkel", "Snorkel"),
                            ("dozer", "Dozer"),
                            ("grader", "Grader"),
                            ("loader", "Loader"),
                            ("tender", "Tender"),
                            ("float", "Float"),
                            ("fixed wing aircraft", "Waterbomber"),
                            ("rotary aircraft", "Rotary"),
                            ("spotter aircraft", "Spotter"),
                            ("helitac", "Helitac"),
                            ("rescue helicopter", "Rescue Helicopter"),
                            ("aviation fuel truck", "Aviation Fuel Truck"),
                            (None, ""),
                            ("comms bus", "Communications Bus"),
                            ("boat", "Boat"),
                            ("person", "Person"),
                            ("other", "Other"),
                            ("unknown", "Unknown"),
                        ],
                        max_length=32,
                    ),
                ),
                ("age", models.FloatField()),
                ("symbolid", models.TextField()),
                (
                    "district",
                    models.CharField(
                        choices=[
                            ("SWAN", "Swan Region"),
                            ("PHD", "Perth Hills"),
                            ("SCD", "Swan Coastal"),
                            ("SWR", "South West Region"),
                            ("BWD", "Blackwood"),
                            ("WTN", "Wellington"),
                            ("WR", "Warren Region"),
                            ("DON", "Donnelly"),
                            ("FRK", "Frankland"),
                            ("SCR", "South Coast Region"),
                            ("ALB", "Albany"),
                            ("ESP", "Esperance"),
                            ("KIMB", "Kimberley Region"),
                            ("EKD", "East Kimberley"),
                            ("WKD", "West Kimberley"),
                            ("PIL", "Pilbara Region"),
                            ("EXM", "Exmouth"),
                            ("GLD", "Goldfields Region"),
                            ("MWR", "Midwest Region"),
                            ("GER", "Geraldton"),
                            ("KLB", "Kalbarri"),
                            ("MOR", "Moora"),
                            ("SHB", "Shark Bay"),
                            ("WBR", "Wheatbelt Region"),
                            ("CWB", "Central Wheatbelt"),
                            ("SWB", "Southern Wheatbelt"),
                            ("AV", "Aviation"),
                            ("OTH", "Other"),
                        ],
                        max_length=32,
                    ),
                ),
                ("district_display", models.CharField(max_length=100)),
                (
                    "source_device_type",
                    models.CharField(
                        choices=[
                            ("tracplus", "TracPlus"),
                            ("iriditrak", "Iriditrak"),
                            ("dplus", "DPlus"),
                            ("spot", "Spot"),
                            ("dfes", "DFES"),
                            ("mp70", "MP70"),
                            ("fleetcare", "Fleetcare"),
                            ("other", "Other"),
                        ],
                        max_length=32,
                    ),
                ),
            ],
            options={
                "verbose_name": "resource",
                "db_table": "tracking_resource_tracking_view",
                "ordering": ("-seen",),
                "managed": False,
            },
        ),
    ]
