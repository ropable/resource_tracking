from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from tracking.admin import tracking_admin_site
from tracking.views import DeviceMetricsSource

admin.site.site_header = "Resource Tracking System administration"
admin.site.index_title = "Resource Tracking System"
admin.site.site_title = "Resource Tracking"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sss_admin/", tracking_admin_site.urls),
    path(
        "api/devices/metrics/<str:source_device_type>/",
        DeviceMetricsSource.as_view(),
        name="device_metrics_source",
    ),
    path("", include("tracking.urls")),
    path("", RedirectView.as_view(pattern_name="admin:index"), name="home"),
]
