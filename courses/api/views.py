from rest_framework import generics
from ..models import Series
from .serializers import SeriesSerializer


class SeriesListView(generics.ListAPIView):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer


class SeriesDetailView(generics.RetrieveAPIView):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer