from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_configs, name="list"),
    path("new/", views.create_config, name="create"),
    path("<int:pk>/edit/", views.edit_config, name="edit"),
]
