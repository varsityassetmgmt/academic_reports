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
from students import tasks
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from usermgmt.models import UserProfile
from django.db.models import Count

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

class ClassNameDropdownForStudentsViewSet(ModelViewSet):
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
    """
    Returns orientations available for students based on user branch access and the current academic year.
    - Superusers see all active branches.
    - Other users see orientations linked to their allowed branches.
    """
    serializer_class = OrientationDropdownSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        # Get current academic year
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        user = self.request.user
        branch_param = self.request.query_params.get('branch_ids')

        # --- Determine accessible branches ---
        if user.groups.filter(id=1).exists():  # super admin
            branches_qs = Branch.objects.filter(is_active=True)
        else:
            # Branches assigned to user via UserProfile
            user_branch_ids = (
                UserProfile.objects.filter(user=user)
                .values_list('branches__branch_id', flat=True)
                .distinct()
            )
            branches_qs = Branch.objects.filter(is_active=True, branch_id__in=user_branch_ids)

        # --- Override with explicit branch_ids param if provided ---
        if branch_param:
            branch_ids = [int(x) for x in branch_param.split(',') if x.isdigit()]
            if branch_ids:
                branches_qs = branches_qs.filter(branch_id__in=branch_ids)

        # --- No valid branches → return none ---
        if not branches_qs.exists():
            return Orientation.objects.none()

        # --- Fetch orientations linked to these branches for the current academic year ---
        orientation_ids = (
            BranchOrientations.objects.filter(
                branch__in=branches_qs,
                academic_year=current_academic_year,
                is_active=True
            )
            .values_list('orientations__orientation_id', flat=True)
            .distinct()
        )

        # --- Return matching orientations ---
        if not orientation_ids:
            return Orientation.objects.none()

        return Orientation.objects.filter(is_active=True, orientation_id__in=orientation_ids).order_by('name')

# ==================== OrientationDropdownForExamViewSet ====================
class OrientationDropdownForExamViewSet(ModelViewSet):
    """
    Returns ONLY the orientations common to *all* selected branches
    (intersection), for the current academic year.
    - Superusers see all active branches.
    - Other users see only their assigned branches via UserProfile.
    """
    serializer_class = OrientationDropdownSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        # --- Get current academic year ---
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        user = self.request.user
        branch_param = self.request.query_params.get("branch_ids")

        # --- Determine accessible branches ---
        if user.groups.filter(id=1).exists():  # super admin
            branches_qs = Branch.objects.filter(is_active=True)
        else:
            user_branch_ids = (
                UserProfile.objects.filter(user=user)
                .values_list("branches__branch_id", flat=True)
                .distinct()
            )
            branches_qs = Branch.objects.filter(is_active=True, branch_id__in=user_branch_ids)

        # --- Override with explicit branch_ids param if provided ---
        if branch_param:
            branch_ids = [int(x) for x in branch_param.split(",") if x.isdigit()]
            if branch_ids:
                branches_qs = branches_qs.filter(branch_id__in=branch_ids)

        # --- No valid branches → return none ---
        if not branches_qs.exists():
            return Orientation.objects.none()

        # --- Compute intersection of orientations across all branches ---
        branch_count = branches_qs.count()

        orientation_ids = (
            BranchOrientations.objects.filter(
                branch__in=branches_qs,
                academic_year=current_academic_year,
                is_active=True
            )
            .values("orientations__orientation_id")
            .annotate(branch_match_count=Count("branch", distinct=True))
            .filter(branch_match_count=branch_count)  # appear in all selected branches
            .values_list("orientations__orientation_id", flat=True)
        )

        if not orientation_ids:
            return Orientation.objects.none()

        return Orientation.objects.filter(
            is_active=True,
            orientation_id__in=orientation_ids
        ).order_by("name")


class OrientationDropdownForStudentsViewSet(ModelViewSet):
    """
    Returns orientations available for students based on user branch access and the current academic year.
    - Superusers see all active branches.
    - Other users see orientations linked to their allowed branches.
    """
    serializer_class = OrientationDropdownSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        # Get current academic year
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        user = self.request.user
        branch_param = self.request.query_params.get('branch_ids')

        # --- Determine accessible branches ---
        if user.groups.filter(id=1).exists():  # super admin
            branches_qs = Branch.objects.filter(is_active=True)
        else:
            # Branches assigned to user via UserProfile
            user_branch_ids = (
                UserProfile.objects.filter(user=user)
                .values_list('branches__branch_id', flat=True)
                .distinct()
            )
            branches_qs = Branch.objects.filter(is_active=True, branch_id__in=user_branch_ids)

        # --- Override with explicit branch_ids param if provided ---
        if branch_param:
            branch_ids = [int(x) for x in branch_param.split(',') if x.isdigit()]
            if branch_ids:
                branches_qs = branches_qs.filter(branch_id__in=branch_ids)

        # --- No valid branches → return none ---
        if not branches_qs.exists():
            return Orientation.objects.none()

        # --- Fetch orientations linked to these branches for the current academic year ---
        orientation_ids = (
            BranchOrientations.objects.filter(
                branch__in=branches_qs,
                academic_year=current_academic_year,
                is_active=True
            )
            .values_list('orientations__orientation_id', flat=True)
            .distinct()
        )

        # --- Return matching orientations ---
        if not orientation_ids:
            return Orientation.objects.none()

        return Orientation.objects.filter(is_active=True, orientation_id__in=orientation_ids).order_by('name')

    
class AdmissionStatusDropdownForStudentsViewSet(ModelViewSet):
    queryset = AdmissionStatus.objects.filter(is_active=True).order_by('admission_status_id')
    serializer_class = AdmissionStatusSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

# ========================== Student ViewSet ==========================
class StudentViewSet(ModelViewSet):
    # queryset = Student.objects.filter().order_by('name')
    serializer_class = StudentSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        'SCS_Number', 'name',
        'branch__name', 'zone__name', 'state__name',
        'student_class__name', 'section__name',
        'admission_status__admission_status',
        'orientation__name'
    ]
    ordering_fields = [
        'SCS_Number', 'name',
        'branch__name', 'zone__name', 'state__name',
        'student_class__name', 'section__name',
        'admission_status__admission_status',
        'orientation__name'
    ]
    filterset_fields=[
        'SCS_Number', 'name',
        'branch', 'branch__state', 'branch__zone',
        'student_class', 'section__name', 'orientation',
        'admission_status',
    ]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(id=1).exists():  # Super admin or system user
            branch_ids = Branch.objects.filter(is_active=True)
        else:
            branch_ids = (
                UserProfile.objects.filter(user=user)
                .values_list('branches', flat=True)
                .distinct()
            )

        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        return (
            Student.objects.filter(
                is_active=True,
                branch__branch_id__in=branch_ids,
                student_class__is_active=True,
                academic_year = current_academic_year,
            )
            # .exclude(admission_status_id=3)
            .order_by('branch', 'student_class__class_sequence', 'orientation', 'section', 'name')
        )

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





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trigger_branch_orientation_sync(request):
    tasks.sync_branch_wise_orientations.delay()
    return Response(
        {"message": "Branch orientation sync task triggered successfully."},
    )
        
class SectionViewSet(ModelViewSet):
    serializer_class = SectionSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        'branch__name', 'zone__name', 'state__name',
        'class_name__name', 'orientation__name', 'name',
    ]
    ordering_fields = [
        'branch__name', 'zone__name', 'state__name',
        'class_name__name', 'orientation__name', 'name',    
        'has_students', 'strength',
    ]
    filterset_fields=[
        'branch', 'branch__state', 'branch__zone',
        'class_name', 'orientation', 'name', 
        'has_students',
    ]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(id=1).exists():  # Super admin or system user
            branch_ids = Branch.objects.filter(is_active=True)
        else:
            branch_ids = (
                UserProfile.objects.filter(user=user)
                .values_list('branches', flat=True)
                .distinct()
            )

        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")
        
        return Section.objects.filter(
            is_active=True, 
            academic_year=current_academic_year, 
            branch__branch_id__in=branch_ids,
            class_name__is_active=True,
        ).order_by(
            'branch',
            'class_name__class_sequence',
            'orientation',
            'name'
        )

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewSection]
        elif self.action == 'create':
            permission_classes = [CanAddSection]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeSection]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

