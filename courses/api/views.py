from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Course, Series
from .permissions import IsEnrolled
from .serializers import (
    CourseSerializer,
    CourseWithContentsSerializer,
    SeriesSerializer,
)


class SeriesListView(generics.ListAPIView):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer


class SeriesDetailView(generics.RetrieveAPIView):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    # Perform read-only action. list() and retreive()
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({"enrolled": True})

    @action(
        detail=True,
        methods=["get"],
        serializer_class=CourseWithContentsSerializer,
        
    )
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# class CourseEnrollView(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = (IsAuthenticated,)

#     def post(self, request, pk, format=None):
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({"enrolled": True})
