# Generated by Django 4.0.2 on 2022-10-11 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_rename_speed_trackpoints_mph_trackpoints_direction_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TrackPoints',
            new_name='TrackPoint',
        ),
    ]
