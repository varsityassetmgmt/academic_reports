from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from usermgmt.models import UserProfile
from .serializers import *
from . models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from usermgmt.custompagination import CustomPagination
from .permissions import *
from rest_framework import permissions, status
from branches.models import *
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

# ---------------- Subject ----------------
class SubjectDropdownViewSet(ModelViewSet):
    queryset = Subject.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectDropdownSerializer
    http_method_names = ['get']

# class SubjectDropdownForExamInstanceViewSet(ModelViewSet):
#     # queryset = Subject.objects.filter(is_active=True).order_by('name')
#     permission_classes = [IsAuthenticated]
#     serializer_class = SubjectDropdownSerializer
#     http_method_names = ['get']

#     def get_queryset(self):
#         exam_id = self.kwargs.get('exam_id')
#         if not exam_id:
#             raise ValidationError({'exam_id': "This field is required in the URL."})
        
#         classes = Exam.objects.filter(exam_id=exam_id).values_list('student_classes', flat=True)
#         subjects =Subject.objects.filter(class_names__in=classes).distinct()

#         return subjects

class SubjectDropdownForExamInstanceViewSet(ModelViewSet):
    """
    Provides a dropdown list of subjects associated with the classes of a given Exam.
    URL pattern: /subject_dropdown_for_exam_instance/<exam_id>/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectDropdownSerializer
    http_method_names = ['get']

    def get_queryset(self):
        exam_id = self.kwargs.get('exam_id')
        if not exam_id:
            raise ValidationError({'exam_id': "This field is required in the URL."})

        # ✅ Get the exam safely (avoids DoesNotExist errors)
        exam = Exam.objects.filter(exam_id=exam_id, is_active=True).prefetch_related('student_classes').first()
        if not exam:
            raise ValidationError({'exam_id': f"Exam with ID {exam_id} not found or inactive."})

        # ✅ Fetch all subjects linked to the exam's classes
        subjects = (
            Subject.objects.filter(
                is_active=True,
                class_names__in=exam.student_classes.all()
            )
            .distinct()
            .order_by('name')
        )

        return subjects


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

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)

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
    queryset = SubjectSkill.objects.filter(is_active=True).order_by('subject')
    serializer_class = SubjectSkillSerializer
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'subject__name']
    filterset_fields = ['subject']
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)

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

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)

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

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)

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
    search_fields = ['subject__name']
    pagination_class = CustomPagination
    lookup_field = 'pk'  # for retrieve/update
    lookup_url_kwarg = 'pk'

    def get_exam_id(self):
        """
        Get exam_id from URL kwargs
        """
        exam_id = self.kwargs.get('exam_id')
        if not exam_id:
            raise ValidationError({"exam_id": "This field is required in the URL."})
        return exam_id

    def get_queryset(self):
        exam_id = self.get_exam_id()
        return ExamInstance.objects.filter(
            exam__exam_id=exam_id,
            is_active=True
        ).order_by('date')

    def perform_create(self, serializer):
        exam_id = self.get_exam_id()
        serializer.save(
            exam_id=exam_id,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        exam_id = self.get_exam_id()
        serializer.save(
            exam_id=exam_id,
            updated_by=self.request.user
        )

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

# class ExamInstanceViewSet(ModelViewSet):
#     serializer_class = ExamInstanceSerializer
#     http_method_names = ['get', 'post', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ['exam__name', 'subject__name']
#     pagination_class = CustomPagination

#     def get_queryset(self):
#         # Only require exam_id for GET (list) requests
#         if self.action == 'list':
#             exam_id = self.request.query_params.get('exam_id')
#             if not exam_id:
#                 raise NotFound("Exam ID is required for listing exam instances.")
            
#             return ExamInstance.objects.filter(
#                 exam__exam_id=exam_id,
#                 is_active=True
#             ).order_by('date')
        
#         # For other actions (retrieve, create, update)
#         return ExamInstance.objects.filter(is_active=True).order_by('date')
    
#     def perform_create(self, serializer):
#         if serializer.is_valid():
#             serializer.save(created_by=self.request.user, updated_by=self.request.user)
#     def perform_update(self, serializer):
#         if serializer.is_valid():
#             serializer.save(updated_by=self.request.user)

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewExamInstance]
#         elif self.action == 'create':
#             permission_classes = [CanAddExamInstance]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeExamInstance]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]

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
    pagination_class = CustomPagination
    lookup_field = 'pk'  # for retrieve/update
    lookup_url_kwarg = 'pk'

    def get_exam_instance_id(self):
        """
        Get exam_instance_id from URL kwargs
        """
        exam_instance_id = self.kwargs.get('exam_instance_id')
        if not exam_instance_id:
            raise ValidationError({"exam_instance_id": "This field is required in the URL."})
        return exam_instance_id

    def get_queryset(self):
        exam_instance_id = self.get_exam_instance_id()
        return ExamSubjectSkillInstance.objects.filter(
            exam_instance__exam_instance_id=exam_instance_id,
            is_active=True
        ).order_by('subject_skill__subject__name')

    def perform_create(self, serializer):
        exam_instance_id = self.get_exam_instance_id()
        serializer.save(
            exam_instance_id=exam_instance_id,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        exam_instance_id = self.get_exam_instance_id()
        serializer.save(
            exam_instance_id=exam_instance_id,
            updated_by=self.request.user
        )

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

# class ExamSubjectSkillInstanceViewSet(ModelViewSet):
#     serializer_class = ExamSubjectSkillInstanceSerializer
#     http_method_names = ['get', 'put']
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = [
#         'exam_instance__exam__name',
#         'subject_skill__subject__name',
#         'subject_skill__skill__name',
#     ]
#     filterset_fields = [
#         'exam_instance',
#         'subject_skill',
#         'has_external_marks',
#         'has_internal_marks',
#         'has_subject_co_scholastic_grade',
#         'is_active',
#     ]
#     pagination_class = CustomPagination

#     def get_queryset(self):
#         """
#         Filter ExamSubjectSkillInstance based on exam_instance_id for list views.
#         """
#         if self.action == 'list':
#             exam_instance_id = self.request.query_params.get('exam_instance_id')
#             if not exam_instance_id:
#                 raise NotFound("Exam Instance ID is required for listing exam subject skill instances.")

#             return ExamSubjectSkillInstance.objects.filter(
#                 exam_instance__exam_instance_id=exam_instance_id,
#                 is_active=True
#             ).order_by('subject_skill__subject__name')

#         # For other actions (retrieve, create, update)
#         return ExamSubjectSkillInstance.objects.filter(is_active=True).order_by('subject_skill__subject__name')
    
#     def perform_create(self, serializer):
#         if serializer.is_valid():
#             serializer.save(created_by=self.request.user, updated_by=self.request.user)
#     def perform_update(self, serializer):
#         if serializer.is_valid():
#             serializer.save(updated_by=self.request.user)

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [CanViewExamSubjectSkillInstance]
#         elif self.action == 'create':
#             permission_classes = [CanAddExamSubjectSkillInstance]
#         elif self.action in ['update', 'partial_update']:
#             permission_classes = [CanChangeExamSubjectSkillInstance]
#         else:
#             permission_classes = [permissions.AllowAny]
#         return [permission() for permission in permission_classes]


class BranchWiseExamResultStatusViewSet(ModelViewSet):
    serializer_class = BranchWiseExamResultStatusSerializer
    http_method_names = ['get', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    pagination_class = CustomPagination
    search_fields = [
        'academic_year__name',
        'branch__name',
        'exam__name',
        'status__name'
    ]

    def get_queryset(self):
        user = self.request.user

        # ✅ Efficient branching logic
        if user.groups.filter(id=1).exists():  # Super admin or system user
            branches = Branch.objects.filter(is_active=True)
        else:
            branches = (
                UserProfile.objects.filter(user=user)
                .values_list('branches', flat=True)
                .distinct()
            )

        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")

        # ✅ Avoid returning inactive or invalid records
        queryset = (
            BranchWiseExamResultStatus.objects.filter(
                is_active=True,
                branch__in=branches,
                academic_year=current_academic_year,
            )
            .select_related('academic_year', 'branch', 'exam', 'status')  # optimization
            .order_by('-updated_at')
        )
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewBranchWiseExamResultStatus]
        elif self.action == 'create':
            permission_classes = [CanAddBranchWiseExamResultStatus]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeBranchWiseExamResultStatus]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

class SectionWiseExamResultStatusViewSet(ModelViewSet):
    """
    Handles viewing and updating Section-wise Exam Result Status entries.
    """
    serializer_class = SectionWiseExamResultStatusSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter]
    pagination_class = CustomPagination

    search_fields = [
        'academic_year__name',
        'branch__name',
        'section__name',
        'exam__name',
        'status__name',
    ]

    def get_queryset(self):
        """
        Filters queryset by branch_id and exam_id passed in the URL.
        """
        branch_id = self.kwargs.get('branch_id')
        exam_id = self.kwargs.get('exam_id')

        if not branch_id:
            raise ValidationError({'branch_id': "This field is required in the URL."})
        if not exam_id:
            raise ValidationError({'exam_id': "This field is required in the URL."})
        
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")
        
        queryset = (
            SectionWiseExamResultStatus.objects.filter(
                is_active=True,
                branch__branch_id=branch_id,
                exam__exam_id=exam_id,
                academic_year=current_academic_year,
            )
            .select_related(
                'academic_year',
                'branch',
                'section',
                'exam',
                'status',
            )
            .order_by('-updated_at')  # show most recent first
        )

        return queryset

    def get_permissions(self):
        """
        Assigns permission classes based on the current action.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewSectionWiseExamResultStatus]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeSectionWiseExamResultStatus]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def update_section_wise_exam_result_status_view(request, branch_id, exam_id):
    """
    Syncs section-wise exam result status from branch-wise exam result status
    for a given branch and exam. 
    - Updates existing records.
    - Creates missing SectionWiseExamResultStatus records if not found.
    """
    if not branch_id:
        raise ValidationError({'branch_id': "This field is required in the URL."})
    if not exam_id:
        raise ValidationError({'exam_id': "This field is required in the URL."})

    # ✅ Get current academic year
    current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
    if not current_academic_year:
        raise NotFound("Current academic year not found.")

    # ✅ Get branch-wise record
    branch_status = BranchWiseExamResultStatus.objects.select_related('branch', 'exam').filter(
        branch__branch_id=branch_id,
        exam__exam_id=exam_id,
        is_active=True,
        academic_year=current_academic_year
    ).first()
    if not branch_status:
        raise ValidationError({'Branch': "No record found for this branch & exam in the current academic year."})

    # ✅ Get exam
    try:
        exam = Exam.objects.get(exam_id=exam_id, academic_year=current_academic_year, is_active=True)
    except Exam.DoesNotExist:
        raise ValidationError({'exam_id': "Invalid Exam ID."})

    # ✅ Get all matching sections
    sections = Section.objects.filter(
        academic_year=current_academic_year,
        branch__branch_id=branch_id,
        class_name__class_name_id__in=exam.student_classes.values_list('class_name_id', flat=True),
        orientation__orientation_id__in=exam.orientations.values_list('orientation_id', flat=True),
        is_active=True
    ).distinct()

    if not sections.exists():
        return Response({
            "success": False,
            "message": "No sections found matching the given branch, exam classes, and orientations."
        }, status=status.HTTP_404_NOT_FOUND)

    # ✅ Bulk update existing records
    existing_records = SectionWiseExamResultStatus.objects.filter(
        section__in=sections,
        branch__branch_id=branch_id,
        exam__exam_id=exam_id,
        is_active=True,
        academic_year=current_academic_year
    )

    updated_count = existing_records.update(
        marks_entry_expiry_datetime=branch_status.marks_entry_expiry_datetime,
        is_visible=branch_status.is_visible,
        updated_at=timezone.now()
    )

    # ✅ Identify sections missing records
    existing_section_ids = existing_records.values_list('section__section_id', flat=True)
    missing_sections = sections.exclude(section_id__in=existing_section_ids)

    created_count = 0
    if missing_sections.exists():
        new_objects = []
        for section in missing_sections:
            new_objects.append(SectionWiseExamResultStatus(
                academic_year=current_academic_year,
                branch=branch_status.branch,
                section=section,
                exam=branch_status.exam,
                marks_entry_expiry_datetime=branch_status.marks_entry_expiry_datetime,
                is_visible=branch_status.is_visible,
                is_active=True,
            ))
        SectionWiseExamResultStatus.objects.bulk_create(new_objects)
        created_count = len(new_objects)

    return Response({
        "success": True,
        "message": (
            f"{updated_count} section-wise exam result records updated, "
            f"{created_count} new records created successfully."
        ),
        "branch": branch_status.branch.name,
        "exam": branch_status.exam.name,
        "academic_year": current_academic_year.name
    }, status=status.HTTP_200_OK)
            

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



#====================================================================================================================================================================
#=========================================================        EXAMS OPERATIONS        ===========================================================================
#====================================================================================================================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import Exam, BranchWiseExamResultStatus
from exams.models import ExamResultStatus
from exams.utils.exam_visibility import *


class ExamMakeVisibleAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        try:
            exam = Exam.objects.get(exam_id = pk)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found"}, status=404)

        result = set_exam_visibility(exam, user=request.user, visible=True)
        status_code = 200 if result["success"] else 400
        return Response(result, status=status_code)



class ExamMakeInvisibleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            exam = Exam.objects.get(exam_id = pk)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found"}, status=404)

        result = set_exam_visibility(exam, user=request.user, visible=False)
        return Response(result, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Exam
from django.utils import timezone

class PublishExamAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        exam_id = request.query_params.get("exam_id")

        if not exam_id:
            return Response({"detail": "exam_id is required."},status=status.HTTP_400_BAD_REQUEST,)
        try:
            exam = Exam.objects.get(exam_id = exam_id)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found."},status=status.HTTP_404_NOT_FOUND,)
    
        if exam.marks_entry_expiry_datetime and exam.marks_entry_expiry_datetime < timezone.now():
            return Response({"message": "Cannot publish. Marks entry expiry datetime has already passed.",},status=status.HTTP_400_BAD_REQUEST,)
         
        try:
            exam_status = ExamStatus.objects.get(id =2)
        except ExamStatus.DoesNotExist:
            return Response({"detail": "ExamStatus with id=2 not found."},status=status.HTTP_400_BAD_REQUEST,)
        
        
        exam.is_visible = True
        exam.exam_status = exam_status
        exam.is_editable  = False
        exam.updated_by = request.user
        exam.save(update_fields=["is_visible", "exam_status","is_editable", "updated_by"])

        branch_updated_count = 0

        with transaction.atomic():
            for branch in exam.branches.all():
                obj, created = BranchWiseExamResultStatus.objects.get_or_create(
                    academic_year =exam.academic_year,
                    branch=branch,
                    exam=exam,
                    defaults={
                        "is_visible": True,
                        "marks_entry_expiry_datetime": exam.marks_entry_expiry_datetime,
                    },
                )
                if not created:
                    obj.is_visible = True
                    obj.marks_entry_expiry_datetime = exam.marks_entry_expiry_datetime
                    obj.save(update_fields=["is_visible", "marks_entry_expiry_datetime"])
                else:
                    branch_updated_count += 1

        return Response({"message": f"Exam '{exam.name}' published successfully.","branches_processed": branch_updated_count,},status=status.HTTP_200_OK,)




class ExpireExamAPIView(APIView):
   
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        exam_id = request.query_params.get("exam_id")
        if not exam_id:
            return Response({"detail": "exam_id is required."},status=status.HTTP_400_BAD_REQUEST,)
        try:
            exam = Exam.objects.get(exam_id=exam_id)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found."},status=status.HTTP_404_NOT_FOUND,)

        now = timezone.now()

        if not exam.marks_entry_expiry_datetime:
            return Response({"message": "This exam has no expiry datetime set."},status=status.HTTP_400_BAD_REQUEST,)

        if exam.marks_entry_expiry_datetime > now:
            return Response({"message": "Exam is still active. Expiry time not reached yet."},status=status.HTTP_400_BAD_REQUEST,)
        
        try:
            locked_status = ExamStatus.objects.get(id = 3)
        except ExamStatus.DoesNotExist:
            return Response({"detail": "ExamStatus 'Marks Entry Locked' not found. Please create it."},status=status.HTTP_400_BAD_REQUEST,)

        exam.is_visible = False
        exam.exam_status = locked_status
        exam.is_editable  = False
        exam.updated_by = request.user
        exam.save(update_fields=["is_visible", "exam_status", "is_editable","updated_by"])
       

        branch_updated_count = 0
        with transaction.atomic():
            branches = BranchWiseExamResultStatus.objects.filter(exam=exam, is_visible=True)
            for branch in branches:
                branch.is_visible = False
                branch.marks_entry_expiry_datetime = exam.marks_entry_expiry_datetime
            BranchWiseExamResultStatus.objects.bulk_update(branches, ["is_visible", "marks_entry_expiry_datetime"])
            branch_updated_count = branches.count()
            # for branch in BranchWiseExamResultStatus.objects.filter(exam=exam, is_visible=True):
            #     branch.is_visible = False
            #     branch.marks_entry_expiry_datetime = exam.marks_entry_expiry_datetime
            #     branch.save(update_fields=["is_visible", "marks_entry_expiry_datetime"])
            #     branch_updated_count += 1

        return Response(
            {
                "message": f"Exam '{exam.name}' expired successfully.",
                "branches_updated": branch_updated_count,
            },
            status=status.HTTP_200_OK,
        )
       
