from django.db import models

# Create your models here.

class Marker(models.Model):
    name = models.CharField(max_length=30)
    uid = models.CharField(max_length=7)
    latitude = models.DecimalField(decimal_places=5, max_digits=7)
    longitude = models.DecimalField(decimal_places=5, max_digits=7)
    caption = models.CharField(max_length=50, null=True, blank=True)

class MapMode(models.Model):
    name = models.CharField(max_length=25)
    value = models.BooleanField()

class Track(models.Model):
    name = models.CharField(max_length=50)
    display = models.BooleanField(default=False)

class TrackPoint(models.Model):
    track_key = models.ForeignKey(Track, on_delete=models.CASCADE,blank=True, null=True)
    mph = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    knts = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    kph = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    direction = models.CharField(max_length=10,blank=True, null=True)
    heading = models.IntegerField(blank=True, null=True)
    time = models.CharField(max_length=5, blank=True, null=True)
    lat = models.DecimalField(max_digits=10, decimal_places=5,blank=True, null=True)
    lon = models.DecimalField(max_digits=10, decimal_places=5,blank=True, null=True)