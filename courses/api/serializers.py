from rest_framework import serializers

from ..models import Course, Series, Module


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ("id", "title", "slug")

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("order", "title", "description")


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = (
            "id",
            "series",
            "title",
            "slug",
            "overview",
            "released_date",
            "owner",
            "modules",
        )

