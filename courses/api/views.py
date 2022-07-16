from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Course, Series
from .serializers import SeriesSerializer


class SeriesListView(generics.ListAPIView):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer


class SeriesDetailView(generics.RetrieveAPIView):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer

class CourseEnrollView(APIView):
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({"enrolled": True})