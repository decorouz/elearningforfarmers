from django.contrib import admin
from .models import Series, Course, Module

# Register your models here.


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title"]


class Moduleinline(admin.TabularInline):
    model = Module
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "series", "released_date"]

    list_filster = ["released_date", "series"]
    autocomplete_fields = ["series"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [Moduleinline]
