from courses.views import CourseListView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="pages/home.html"),
        name="home",
    ),
    # User management
    path(
        "users/",
        include("users.urls", namespace="users"),
    ),
    path("accounts/", include("allauth.urls")),
    # Course management
    path("courses/", include("courses.urls")),
    # Student management
    path("students/", include("students.urls")),
    # Django admin
    path("admin/", admin.site.urls),
    # Rest Api
    path("api/v1/", include("courses.api.urls", namespace="api")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/dj-rest-auth/", include("dj_rest_auth.urls")),
    path(
        "api/v1/dj-rest-auth/registration/",
        include("dj_rest_auth.registration.urls"),
    ),
]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
