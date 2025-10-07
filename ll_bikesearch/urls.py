"""Defines URL patterns for learning_logs."""

from django.urls import path

from . import views

app_name = 'll_bikesearch'

urlpatterns = [
    # Bike Search Page
path('ll_bikesearch/', views.bikesearch, name='bikesearch'),
]