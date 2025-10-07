"""Defines URL patterns for the bike dashboard."""

from django.urls import path

from . import views

app_name = 'bikedash'

urlpatterns = [
    
    # Bike Dashboard
    path('', views.bikedash, name='bikedash'),
    path("<int:pk>/set-default/", views.set_default_bike, name="set_default_bike"),
    path("<int:pk>/delete/", views.delete_bike, name="delete_bike"), 

]