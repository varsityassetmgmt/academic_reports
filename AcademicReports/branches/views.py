from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Create your views here.
class AcademicDevisionDropdownViewSet(ModelViewSet):
    queryset = AcademicDevision.objects.filter(is_active=True).order_by('academic_devision_id')
    permission_classes = [IsAuthenticated]
    serializer_class = AcademicDevisionDropdownSerializer
    http_method_names = ['get',]

class AcademicYearDropdownViewSet(ModelViewSet):
    queryset = AcademicYear.objects.filter(is_active=True).order_by('-academic_year_id')
    permission_classes = [IsAuthenticated]
    serializer_class = AcademicYearDropdownSerialzier
    http_method_names = ['get',]


class StateDropdownViewSet(ModelViewSet):
    queryset = State.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = StateDropdownSerializer
    http_method_names = ['get',]

class StateDropdownForExamViewSet(ModelViewSet):
    queryset = State.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = StateDropdownSerializer
    http_method_names = ['get',]


class ZoneDropdownViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ZoneDropdownSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        # Get 'state_ids' query parameter (comma-separated)
        state_ids_str = self.request.GET.get('state_ids', '')  # e.g., "1,2,3" or empty
        queryset = Zone.objects.filter(is_active=True).order_by('name')

        if state_ids_str.strip():  # Only exclude if non-empty
            try:
                state_ids = [int(sid) for sid in state_ids_str.split(',') if sid.isdigit()]
                if state_ids:
                    queryset = queryset.filter(state__state_id__in=state_ids)
            except ValueError:
                pass  # Ignore invalid input

        return queryset

class ZoneDropdownForExamViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ZoneDropdownSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        # Get 'state_ids' query parameter (comma-separated)
        state_ids_str = self.request.GET.get('state_ids', '')  # e.g., "1,2,3" or empty
        queryset = Zone.objects.filter(is_active=True).order_by('name')

        if state_ids_str.strip():  # Only exclude if non-empty
            try:
                state_ids = [int(sid) for sid in state_ids_str.split(',') if sid.isdigit()]
                if state_ids:
                    queryset = queryset.filter(state__state_id__in=state_ids)
            except ValueError:
                pass  # Ignore invalid input

        return queryset

class BranchDropdownViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BranchDropdownSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        # Get query params
        state_ids_str = self.request.GET.get('state_ids', '')  # e.g., "1,2,3"
        zone_ids_str = self.request.GET.get('zone_ids', '')    # e.g., "5,7"

        queryset = Branch.objects.filter(is_active=True).order_by('name')

        # Exclude branches based on state_ids
        if state_ids_str.strip():
            try:
                state_ids = [int(sid) for sid in state_ids_str.split(',') if sid.isdigit()]
                if state_ids:
                    queryset = queryset.filter(state__state_id__in=state_ids)
            except ValueError:
                pass  # Ignore invalid input

        # Exclude branches based on zone_ids
        if zone_ids_str.strip():
            try:
                zone_ids = [int(zid) for zid in zone_ids_str.split(',') if zid.isdigit()]
                if zone_ids:
                    queryset = queryset.filter(zone__zone_id__in=zone_ids)
            except ValueError:
                pass  # Ignore invalid input

        return queryset

class BranchDropdownForExamViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BranchDropdownSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        # Get query params
        state_ids_str = self.request.GET.get('state_ids', '')  # e.g., "1,2,3"
        zone_ids_str = self.request.GET.get('zone_ids', '')    # e.g., "5,7"

        queryset = Branch.objects.filter(is_active=True).order_by('name')

        # Exclude branches based on state_ids
        if state_ids_str.strip():
            try:
                state_ids = [int(sid) for sid in state_ids_str.split(',') if sid.isdigit()]
                if state_ids:
                    queryset = queryset.filter(state__state_id__in=state_ids)
            except ValueError:
                pass  # Ignore invalid input

        # Exclude branches based on zone_ids
        if zone_ids_str.strip():
            try:
                zone_ids = [int(zid) for zid in zone_ids_str.split(',') if zid.isdigit()]
                if zone_ids:
                    queryset = queryset.filter(zone__zone_id__in=zone_ids)
            except ValueError:
                pass  # Ignore invalid input

        return queryset