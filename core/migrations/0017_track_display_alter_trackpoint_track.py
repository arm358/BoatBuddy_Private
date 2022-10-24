# Generated by Django 4.0.2 on 2022-10-11 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_trackpoints_trackpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='display',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='trackpoint',
            name='track',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.track'),
        ),
    ]
