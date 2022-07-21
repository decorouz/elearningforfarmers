from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "courses"


router = routers.DefaultRouter()
router.register("courses", views.CourseViewSet)

urlpatterns = [
    path(
        "series/",
        views.SeriesListView.as_view(),
        name="series_list",
    ),
    path(
        "series/<pk>/",
        views.SeriesDetailView.as_view(),
        name="series_detail",
    ),
    path("", include(router.urls)),
]
