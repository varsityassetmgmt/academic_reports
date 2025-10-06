from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import ClassName, Orientation
from .serializers import *
from usermgmt.custompagination import CustomPagination
from .permmissions import *
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound

# Create your views here.
class ClassNameDropdownViewSet(ModelViewSet):
    queryset = ClassName.objects.filter(is_active=True).order_by('class_sequence')
    permission_classes = [IsAuthenticated]
    serializer_class = ClassNameDropdownSerializer
    http_method_names = ['get',]

# ==================== ClassNameDropdownForExamViewSet ====================
class ClassNameDropdownForExamViewSet(ModelViewSet):
    serializer_class = ClassNameDropdownSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        queryset = ClassName.objects.filter(is_active=True).order_by('class_sequence')

        # Optional filters:
        # - Single:  ?academic_division_id=3
        # - Multiple: ?academic_division_ids=1,2,3
        academic_division_id = self.request.query_params.get('academic_division_id')
        academic_division_ids = self.request.query_params.get('academic_division_ids')

        # Handle multiple academic division IDs
        if academic_division_ids:
            ids = [int(x) for x in academic_division_ids.split(',') if x.isdigit()]
            if ids:
                queryset = ClassName.objects.filter(
                    is_active=True,
                    academicdevision__in=ids  # reverse M2M lookup
                ).distinct().order_by('class_sequence')
            else:
                queryset = ClassName.objects.none()

        # Handle single academic division ID (for backward compatibility)
        elif academic_division_id:
            try:
                division = AcademicDevision.objects.get(pk=academic_division_id)
                queryset = division.classes.filter(is_active=True).order_by('class_sequence')
            except AcademicDevision.DoesNotExist:
                queryset = ClassName.objects.none()

        return queryset


class OrientationDropdownViewSet(ModelViewSet):
    queryset = Orientation.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = OrientationDropdownSerializer
    http_method_names = ['get',]

# ==================== OrientationDropdownForExamViewSet ====================
class OrientationDropdownForExamViewSet(ModelViewSet):
    serializer_class = OrientationDropdownSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Orientation.objects.filter(is_active=True).order_by('name')
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        # Collect all branch IDs from filters
        branch_ids = set()

        state_ids = self.request.query_params.get('state_ids')
        zone_ids = self.request.query_params.get('zone_ids')
        direct_branch_ids = self.request.query_params.get('branch_ids')

        # If none of the filters provided → return empty queryset
        if not (state_ids or zone_ids or direct_branch_ids):
            return Orientation.objects.none()

        # Filter by states
        if state_ids:
            state_ids = [int(x) for x in state_ids.split(',') if x.isdigit()]
            if state_ids:
                branch_ids.update(
                    Branch.objects.filter(state__state_id__in=state_ids, is_active=True)
                    .values_list('branch_id', flat=True)
                )

        # Filter by zones
        if zone_ids:
            zone_ids = [int(x) for x in zone_ids.split(',') if x.isdigit()]
            if zone_ids:
                branch_ids.update(
                    Branch.objects.filter(zone__zone_id__in=zone_ids, is_active=True)
                    .values_list('branch_id', flat=True)
                )

        # Filter by explicit branch IDs
        if direct_branch_ids:
            direct_branch_ids = [int(x) for x in direct_branch_ids.split(',') if x.isdigit()]
            branch_ids.update(direct_branch_ids)

        # If no filters provided → return all active orientations
        if not (state_ids or zone_ids or direct_branch_ids):
            return queryset

        # If filters provided but no branches found → return empty queryset
        if not branch_ids:
            return Orientation.objects.none()

        # If any branches found, filter orientations linked to them
        orientation_ids = (
            BranchOrientations.objects.filter(
                branch__branch_id__in=branch_ids,
                academic_year=current_academic_year,
                is_active=True
            )
            .values_list('orientations__orientation_id', flat=True)
            .distinct()
        )

        if orientation_ids:
            queryset = queryset.filter(orientation_id__in=orientation_ids)
        else:
            queryset = Orientation.objects.none()

        return queryset

# ========================== Student ViewSet ==========================
class StudentViewSet(ModelViewSet):
    queryset = Student.objects.filter().order_by('name')
    serializer_class = StudentSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'SCS_Number', 'name', 'varna_student_id',
        'branch__name', 'zone__name', 'state__name',
        'student_class__name', 'section__name',
        'gender__name', 'admission_status__admission_status',
        'orientation__name'
    ]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewStudent]
        elif self.action == 'create':
            permission_classes = [CanAddStudent]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeStudent]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

