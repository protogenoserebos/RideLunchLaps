from django.urls import path
from . import views

app_name = "bikeprofile"

urlpatterns = [
    path("p/@<str:username>/<slug:slug>/", views.bike_detail_by_slug, name="detail"),
    path("p/<uuid:public_id>/", views.bike_detail_public, name="detail_public"),
]
