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

class OrientationDropdownForExamViewSet(ModelViewSet):
    queryset = Orientation.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = OrientationDropdownSerializer
    http_method_names = ['get',]

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

