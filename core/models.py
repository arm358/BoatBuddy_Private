from django.db import models

# Create your models here.

class Marker(models.Model):
    name = models.CharField(max_length=30)
    uid = models.CharField(max_length=7)
    latitude = models.DecimalField(decimal_places=5, max_digits=7)
    longitude = models.DecimalField(decimal_places=5, max_digits=7)
    caption = models.CharField(max_length=50, null=True, blank=True)

class MapMode(models.Model):
    name = models.CharField(max_length=5)
    dark = models.BooleanField()

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
    """
    "mph": knots_to_mph(float(gps.speed_knots)),
    "knts": round(float(gps.speed_knots),2),
    "kph": knots_to_kph(float(gps.speed_knots)),
    "direction": get_cardinal(gps.track_angle_deg, gps.speed_knots),
    "heading": heading_cleanser(gps.track_angle_deg, gps.speed_knots),
    "depth": 0,
    "air": 0,
    "humidity": 0,
    "time": ctime.strftime("%H:%M"),
    "tide_type": type,
    "tide_time": tide_time,
    "heights": heights,
    "times": times,
    "lat": lat,
    "lon": lon,
    "track": track_history[:-4],
    """