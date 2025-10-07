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
from branches.models import *
from rest_framework.exceptions import NotFound

# ---------------- Subject ----------------
class SubjectDropdownViewSet(ModelViewSet):
    queryset = Subject.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectDropdownSerializer
    http_method_names = ['get']

class SubjectDropdownForExamInstanceViewSet(ModelViewSet):
    queryset = Subject.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectDropdownSerializer
    http_method_names = ['get']


# ---------------- SubjectSkill ----------------
class SubjectSkillDropdownViewSet(ModelViewSet):
    queryset = SubjectSkill.objects.filter(is_active=True).order_by('subject')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSkillDropdownSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['subject']

class SubjectSkillDropdownForExamInstanceViewSet(ModelViewSet):
    queryset = SubjectSkill.objects.filter(is_active=True).order_by('subject')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSkillDropdownSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['subject']


# ---------------- ExamType ----------------
class ExamTypeDropdownViewSet(ModelViewSet):
    queryset = ExamType.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = ExamTypeDropdownSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = []

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
    filterset_fields = ['academic_devisions', 'class_names', ]
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
    filterset_fields = ['subject']
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
    serializer_class = ExamSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'exam_type__name', 'academic_year__name']
    filterset_fields = ['exam_type', 'is_visible']
    ordering = ['-start_date', 'is_visible']
    pagination_class = CustomPagination

    def get_queryset(self):
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")
        
        exams = Exam.objects.filter(
            academic_year=current_academic_year,
            is_active=True
        ).order_by('-start_date')
        return exams

    def perform_create(self, serializer):
        """
        Automatically assign the current academic year when creating a new exam.
        """
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        serializer.save(academic_year=current_academic_year)

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
    serializer_class = ExamInstanceSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['exam__name', 'subject__name']
    pagination_class = CustomPagination

    def get_queryset(self):
        # Only require exam_id for GET (list) requests
        if self.action == 'list':
            exam_id = self.request.query_params.get('exam_id')
            if not exam_id:
                raise NotFound("Exam ID is required for listing exam instances.")
            
            return ExamInstance.objects.filter(
                exam__exam_id=exam_id,
                is_active=True
            ).order_by('date')
        
        # For other actions (retrieve, create, update)
        return ExamInstance.objects.filter(is_active=True).order_by('date')

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

# ==================== ExamSubjectSkillInstance ====================
class ExamSubjectSkillInstanceViewSet(ModelViewSet):
    serializer_class = ExamSubjectSkillInstanceSerializer
    http_method_names = ['get', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        'exam_instance__exam__name',
        'subject_skill__subject__name',
        'subject_skill__skill__name',
    ]
    filterset_fields = [
        'exam_instance',
        'subject_skill',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_co_scholastic_grade',
        'is_active',
    ]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Filter ExamSubjectSkillInstance based on exam_instance_id for list views.
        """
        if self.action == 'list':
            exam_instance_id = self.request.query_params.get('exam_instance_id')
            if not exam_instance_id:
                raise NotFound("Exam Instance ID is required for listing exam subject skill instances.")

            return ExamSubjectSkillInstance.objects.filter(
                exam_instance__exam_instance_id=exam_instance_id,
                is_active=True
            ).order_by('subject_skill__subject__name')

        # For other actions (retrieve, create, update)
        return ExamSubjectSkillInstance.objects.filter(is_active=True).order_by('subject_skill__subject__name')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewExamSubjectSkillInstance]
        elif self.action == 'create':
            permission_classes = [CanAddExamSubjectSkillInstance]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeExamSubjectSkillInstance]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

# # ==================== ExamAttendanceStatus ====================
# class ExamAttendanceStatusViewSet(ModelViewSet):
#     queryset = ExamAttendanceStatus.objects.filter(is_active=True).order_by('name')
#     serializer_class = ExamAttendanceStatusSerializer
#     http_method_names = ['get', 'post', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ['name', 'short_code']
#     pagination_class = CustomPagination

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewExamAttendanceStatus]
#         elif self.action == 'create':
#             permission_classes = [CanAddExamAttendanceStatus]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeExamAttendanceStatus]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]


# # ==================== GradeBoundary ====================
# class GradeBoundaryViewSet(ModelViewSet):
#     queryset = GradeBoundary.objects.filter(is_active=True).order_by('-min_percentage')
#     serializer_class = GradeBoundarySerializer
#     http_method_names = ['get', 'post', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ['grade', 'exam_type__name', 'orientation__name']
#     pagination_class = CustomPagination

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewGradeBoundary]
#         elif self.action == 'create':
#             permission_classes = [CanAddGradeBoundary]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeGradeBoundary]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]


# # ==================== ExamResult ====================
# class ExamResultViewSet(ModelViewSet):
#     queryset = ExamResult.objects.filter(is_active=True).order_by('-id')
#     serializer_class = ExamResultSerializer
#     http_method_names = ['get', 'post', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ['student__SCS_Number', 'student__name', 'exam_instance__exam__name']
#     pagination_class = CustomPagination

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewExamResult]
#         elif self.action == 'create':
#             permission_classes = [CanAddExamResult]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeExamResult]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]


# # ==================== ExamSkillResult ====================
# class ExamSkillResultViewSet(ModelViewSet):
#     queryset = ExamSkillResult.objects.all()
#     serializer_class = ExamSkillResultSerializer
#     http_method_names = ['get', 'post', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ['exam_result__student__name', 'skill__name']
#     pagination_class = CustomPagination

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewExamSkillResult]
#         elif self.action == 'create':
#             permission_classes = [CanAddExamSkillResult]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeExamSkillResult]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]


# # ==================== StudentExamSummary ====================
# class StudentExamSummaryViewSet(ModelViewSet):
#     queryset = StudentExamSummary.objects.filter(is_active=True).order_by('-id')
#     serializer_class = StudentExamSummarySerializer
#     http_method_names = ['get', 'post', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ['student__SCS_Number', 'student__name', 'exam__name']
#     pagination_class = CustomPagination

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewStudentExamSummary]
#         elif self.action == 'create':
#             permission_classes = [CanAddStudentExamSummary]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeStudentExamSummary]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]
