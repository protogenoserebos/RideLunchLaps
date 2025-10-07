"""URL patterns for ll_buildbike."""

from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import BikeCreateWizard, BikeEditWizard, home

app_name = "ll_buildbike"

urlpatterns = [
    # Homepage
    path("", views.home, name="home"),

    # Bike Builder (single-form flow)
    path("bikebuilder/", views.bikebuild, name="bikebuilder"),

    # Optional: search page (you already have the view)
    path("bikes/search/", views.bikesearch, name="bikesearch"),

    # Bike Creation Wizard (uses form_list defined on the class)
    path("bikes/new/", BikeCreateWizard.as_view(), name="bike_wizard"),

    path("bikes/<int:pk>/edit/", BikeEditWizard.as_view(), name="bike_wizard_edit"), 
    
     path("bikes/<int:pk>/like/", views.toggle_like, name="toggle_like"), 
]

# Serve media files in development (images uploaded during the wizard)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
