from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *

# Create your views here.
class AcademicDevisionDropdownViewSet(ModelViewSet):
    queryset = AcademicDevision.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = AcademicDevisionDropdownSerializer
    http_method_names = ['GET',]


class StateDropdownViewSet(ModelViewSet):
    queryset = State.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = StateDropdownSerializer
    http_method_names = ['GET',]


class ZoneDropdownViewSet(ModelViewSet):
    queryset = Zone.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = ZoneDropdownSerializer
    http_method_names = ['GET',]


class BranchDropdownViewSet(ModelViewSet):
    queryset = Branch.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = BranchDropdownSerializer
    http_method_names = ['GET',]
