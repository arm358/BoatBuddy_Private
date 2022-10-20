from django.contrib import admin
from .models import *

class MarkerAdmin(admin.ModelAdmin):
    model = Marker
    list_display = ["name", "latitude","longitude"]

admin.site.register(Marker, MarkerAdmin)
admin.site.register(MapMode)
admin.site.register(Track)
admin.site.register(TrackPoint)