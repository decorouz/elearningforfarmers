from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.cache import cache
from django.db.models import Count
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from students.forms import CourseEnrollForm

from courses.models import Course

from .forms import ModuleInlineFormSet
from .models import Content, Module, Series


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


class CourseModuleUpdateView(LoginRequiredMixin, TemplateResponseMixin, View):
    """Handles the formset to add, update and delete modules for specific course"""

    template_name = "courses/manage/module/formset.html"
    course = None

    def get_formset(self, data=None):
        return ModuleInlineFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        try:
            self.course = get_object_or_404(Course, id=pk, owner=request.user)
        except Exception as e:
            None

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


# Adding content to course modules.
# There are four different content types.
class ContentCreateUpdateView(LoginRequiredMixin, TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name: str = "courses/manage/content/form.html"

    def get_model(self, model_name):
        if model_name in ["text", "video", "image", "file"]:
            return apps.get_model(app_label="courses", model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):

        Form = modelform_factory(
            model, exclude=["creator", "order", "created", "updated"]
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):

        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)

        if id:
            self.obj = get_object_or_404(
                self.model, id=id, creator=request.user
            )
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({"form": form, "object": self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(
            self.model,
            instance=self.obj,
            data=request.POST,
            files=request.FILES,
        )

        if form.is_valid():
            obj = form.save(commit=False)
            obj.creator = request.user
            obj.save()

            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect("courses:module_content_list", self.module.id)
        return self.render_to_response({"form": form, "object": self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user
        )

        module = content.module
        content.item.delete()
        content.delete()
        return redirect("courses:module_content_list", module.id)


class ModuleContentListView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "courses/manage/module/content_list.html"

    def get(self, request, module_id):
        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )

        return self.render_to_response({"module": module})


# You need a view that recieves the new order of module IDs
# encoded in JSON


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    """Module that orders the course module"""

    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(
                order=order
            )
        return self.render_json_response({"saved": "OK"})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    """View to order module content"""

    def post(self, request):
        for id, order in self.request_json.items():

            Content.objects.filter(
                id=id, module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({"saved": "OK"})


# Creating public views for displaying course information

# -----List all available courses and optionall filter by series


class CourseListView(TemplateResponseMixin, View):
    """List all available course, optionally filter by subject"""

    model = Course
    template_name = "courses/course/list.html"

    def get(self, request, subject=None):
        # retrieve all series, including the total number of courses for each series

        # series = Series.objects.annotate(total_courses=Count("courses"))

        series = cache.get("all_series")
        if not series:
            series = Series.objects.annotate(total_courses=Count("courses"))
            cache.set("all_series", series)

        # retrieve all courses, including the total number of modules contained in each course
        all_courses = Course.objects.annotate(total_modules=Count("modules"))

        if subject:
            subject = get_object_or_404(Series, slug=subject)

            key = f"subject_{subject.id}_courses"
            courses = cache.get(key)

            if not courses:
                courses = all_courses.filter(series=subject)
                cache.set(key, courses)
        else:
            courses = cache.get("all_courses")
            if not courses:
                courses = all_courses
                cache.set("all_courses", courses)

        return self.render_to_response(
            {"series": series, "subject": subject, "courses": courses}
        )


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course/detail.html"

    def get_context_data(self, **kwargs):
        """Used to populate a dictionary to use as a template context"""
        context = super().get_context_data(**kwargs)

        context["enroll_form"] = CourseEnrollForm(
            initial={"course": self.object}
        )
        return context
