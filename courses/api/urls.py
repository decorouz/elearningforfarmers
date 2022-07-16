from django.urls import path

from . import views

app_name = "courses"

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
    path(
        "courses/<pk>/enroll/",
        views.CourseEnrollView.as_view(),
        name="course_enroll",
    ),
]
