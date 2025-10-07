"""Defines URL patterns for learning_logs."""

from django.urls import path

from . import views

app_name = 'bikeaggr'

urlpatterns = [
    # Bike Aggregator Page for PinkBike results
    path('bikeaggr/', views.bikesearchagg, name='bikesearchagg'),

]