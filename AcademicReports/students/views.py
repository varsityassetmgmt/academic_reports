from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import ClassName, Orientation
from .serializers import *
# Create your views here.
class ClassNameDropdownViewSet(ModelViewSet):
    queryset = ClassName.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = ClassNameDropdownSerializer


class OrientationDropdownViewSet(ModelViewSet):
    queryset = Orientation.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = OrientationDropdownSerializer
