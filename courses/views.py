from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from .forms import ModuleInlineFormSet

from courses.models import Course

# Create your views here.
class HomeView(ListView):
    model = Course
    template_name = "home.html"


class OwnerMixin(object):
    def get_queryset(self):
        """Get the base Queryset"""
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    """Implement form that is used by views that use
    Django's ModelFormMixin mixin. View with form or model form.
    e.g CreateView and UpdateView"""

    def form_valid(self, form):
        # Executed when the submitted form is valid
        """set the owner of an object automatically when it is saved"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(
    OwnerMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    model = Course
    fields = ["series", "title", "slug", "overview"]
    success_url = reverse_lazy("courses:manage_course_list")


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = "courses/manage/course/form.html"


class ManageCourseList(OwnerCourseMixin, ListView):
    """Retrieve only courses created by the current user"""

    template_name = "courses/manage/course/list.html"
    permission_required = "courses.view_course"
    context_object_name = "my_courses"


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = "courses.add_course"


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = "courses.change_course"


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = "courses/manage/course/delete.html"
    permission_required = "courses.delete_course"


class CourseModuleUpdateView(TemplateResponseMixin, View):
    """Handles the formset to add, update and delete modules for specific course"""

    template_name = "courses/manage/module/formset.html"
    course = None

    def get_formset(self, data=None):
        return ModuleInlineFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {"course": self.course, "formset": formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("courses:manage_course_list")
        return self.render_to_response(
            {"course": self.course, "formset": formset}
        )


# Functional based view
