from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("record/", views.record_track, name="record"),
    path("save-track/", views.save_track, name="save_track"),
    path("clear-progress/", views.clear_progress, name="clear_progress"),
    path("shutdown/", views.shutdown, name="shutdown"),
    path("customize/", views.customize, name="customize"),
    path("delete/", views.delete_file, name="delete"),
    path("deletemarker/", views.delete_marker, name="delete_marker"),
    path("addmarker/", views.add_marker, name="add_marker"),
    path("download/<file>", views.download_file, name="download"),
    path("timeconfig/", views.update_time_config, name="timeconfig"),
    path("mapmodeconfig/", views.update_map_mode, name="mapmodeconfig"),
    path("tidedata/", views.update_tide_data, name="tidedata")
]
