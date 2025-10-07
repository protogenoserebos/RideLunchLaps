from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from ll_buildbike.views import home

urlpatterns = [
    path("", home, name="home"),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("ll_buildbike/", include(("ll_buildbike.urls", "ll_buildbike"), namespace="ll_buildbike")),
    path("bikedash/", include(("bikedash.urls", "bikedash"), namespace="bikedash")),
    path("bikeconfigs/", include(("bikeconfigs.urls", "bikeconfigs"), namespace="bikeconfigs")),
    path("ll_bikesearch/", include("ll_bikesearch.urls")),
    path("bikeaggr/", include("bikeaggr.urls")),
    path("admin/", admin.site.urls),
    path("p/", include(("bikeprofile.urls", "bikeprofile"), namespace="bikeprofile")),
    path("", include(("bikeprofile.urls", "bikeprofile"), namespace="bikeprofile")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
