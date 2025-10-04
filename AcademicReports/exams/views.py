from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from . models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from usermgmt.custompagination import CustomPagination
from .permissions import *
from rest_framework import permissions, status

# ---------------- Subject ----------------
class SubjectDropdownViewSet(ModelViewSet):
    queryset = Subject.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectDropdownSerializer
    http_method_names = ['get']


# ---------------- SubjectSkill ----------------
class SubjectSkillDropdownViewSet(ModelViewSet):
    queryset = SubjectSkill.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSkillDropdownSerializer
    http_method_names = ['get']


# ---------------- ExamType ----------------
class ExamTypeDropdownViewSet(ModelViewSet):
    queryset = ExamType.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = ExamTypeDropdownSerializer
    http_method_names = ['get']


# ---------------- Exam ----------------
class ExamDropdownViewSet(ModelViewSet):
    queryset = Exam.objects.filter(is_active=True).order_by('-start_date')
    permission_classes = [IsAuthenticated]
    serializer_class = ExamDropdownSerializer
    http_method_names = ['get']


# ---------------- ExamInstance ----------------
class ExamInstanceDropdownViewSet(ModelViewSet):
    queryset = ExamInstance.objects.filter(is_active=True).order_by('-date')
    permission_classes = [IsAuthenticated]
    serializer_class = ExamInstanceDropdownSerializer
    http_method_names = ['get']


# ---------------- ExamAttendanceStatus ----------------
class ExamAttendanceStatusDropdownViewSet(ModelViewSet):
    queryset = ExamAttendanceStatus.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = ExamAttendanceStatusDropdownSerializer
    http_method_names = ['get']

# ==================== Subject ====================
class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.filter(is_active=True).order_by('name')
    serializer_class = SubjectSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'display_name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewSubject]
        elif self.action == 'create':
            permission_classes = [CanAddSubject]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeSubject]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== SubjectSkill ====================
class SubjectSkillViewSet(ModelViewSet):
    queryset = SubjectSkill.objects.filter(is_active=True).order_by('name')
    serializer_class = SubjectSkillSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'subject__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewSubjectSkill]
        elif self.action == 'create':
            permission_classes = [CanAddSubjectSkill]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeSubjectSkill]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== ExamType ====================
class ExamTypeViewSet(ModelViewSet):
    queryset = ExamType.objects.filter(is_active=True).order_by('name')
    serializer_class = ExamTypeSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExamType]
        elif self.action == 'create':
            permission_classes = [CanAddExamType]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExamType]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== Exam ====================
class ExamViewSet(ModelViewSet):
    queryset = Exam.objects.filter(is_active=True).order_by('-start_date')
    serializer_class = ExamSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'exam_type__name', 'academic_year__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExam]
        elif self.action == 'create':
            permission_classes = [CanAddExam]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExam]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== ExamInstance ====================
class ExamInstanceViewSet(ModelViewSet):
    queryset = ExamInstance.objects.filter(is_active=True).order_by('date')
    serializer_class = ExamInstanceSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['exam__name', 'subject__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExamInstance]
        elif self.action == 'create':
            permission_classes = [CanAddExamInstance]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExamInstance]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== ExamAttendanceStatus ====================
class ExamAttendanceStatusViewSet(ModelViewSet):
    queryset = ExamAttendanceStatus.objects.filter(is_active=True).order_by('name')
    serializer_class = ExamAttendanceStatusSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'short_code']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExamAttendanceStatus]
        elif self.action == 'create':
            permission_classes = [CanAddExamAttendanceStatus]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExamAttendanceStatus]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== GradeBoundary ====================
class GradeBoundaryViewSet(ModelViewSet):
    queryset = GradeBoundary.objects.filter(is_active=True).order_by('-min_percentage')
    serializer_class = GradeBoundarySerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['grade', 'exam_type__name', 'orientation__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewGradeBoundary]
        elif self.action == 'create':
            permission_classes = [CanAddGradeBoundary]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeGradeBoundary]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== ExamResult ====================
class ExamResultViewSet(ModelViewSet):
    queryset = ExamResult.objects.filter(is_active=True).order_by('-id')
    serializer_class = ExamResultSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['student__SCS_Number', 'student__name', 'exam_instance__exam__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExamResult]
        elif self.action == 'create':
            permission_classes = [CanAddExamResult]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExamResult]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== ExamSkillResult ====================
class ExamSkillResultViewSet(ModelViewSet):
    queryset = ExamSkillResult.objects.all()
    serializer_class = ExamSkillResultSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['exam_result__student__name', 'skill__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExamSkillResult]
        elif self.action == 'create':
            permission_classes = [CanAddExamSkillResult]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExamSkillResult]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


# ==================== StudentExamSummary ====================
class StudentExamSummaryViewSet(ModelViewSet):
    queryset = StudentExamSummary.objects.filter(is_active=True).order_by('-id')
    serializer_class = StudentExamSummarySerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['student__SCS_Number', 'student__name', 'exam__name']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewStudentExamSummary]
        elif self.action == 'create':
            permission_classes = [CanAddStudentExamSummary]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeStudentExamSummary]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
