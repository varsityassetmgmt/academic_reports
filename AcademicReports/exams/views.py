from django.shortcuts import get_object_or_404, render
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
#             return Response({'exam_id': "This field is required in the URL."}, status=status.HTTP_400_BAD_REQUEST)
        
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
            return Response({'exam_id': "This field is required in the URL."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Get the exam safely (avoids DoesNotExist errors)
        exam = Exam.objects.filter(exam_id=exam_id, is_active=True).prefetch_related('student_classes').first()
        if not exam:
            return Response({'exam_id': f"Exam with ID {exam_id} not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)

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
    search_fields = ['name', 'display_name', 'description']  # text fields to search
    filterset_fields = ['academic_devisions', 'class_names', 'is_active']  # FK/many2many and boolean
    ordering_fields = ['name', 'display_name', 'created_at', 'updated_at']  # fields users can order by
    pagination_class = CustomPagination

    def perform_create(self, serializer):
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
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
    search_fields = ['name', 'subject__name']  # searchable text fields
    filterset_fields = ['subject', 'is_active']  # FK and boolean fields
    ordering_fields = ['name', 'subject__name', 'created_at', 'updated_at']  # sortable fields
    pagination_class = CustomPagination

    def perform_create(self, serializer):
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
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
    search_fields = ['name', 'description']       # text search
    filterset_fields = ['is_active']             # boolean filter
    ordering_fields = ['name', 'created_at', 'updated_at']  # sortable fields
    pagination_class = CustomPagination

    def perform_create(self, serializer):
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
    def perform_update(self, serializer):
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
    filterset_fields = [
        'exam_type', 'is_visible', 'is_progress_card_visible',
        'is_active', 'academic_year', 'name', 'start_date',
        'end_date', 'marks_entry_expiry_datetime',
    ]
    ordering_fields = [
        'exam_type__name', 'start_date', 'end_date', 'name',
        'is_visible', 'created_at', 'updated_at',
        'academic_year', 'marks_entry_expiry_datetime',
    ]
    pagination_class = CustomPagination

    def get_queryset(self):
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")
        return Exam.objects.filter(
            academic_year=current_academic_year,
            is_active=True
        ).order_by('-exam_id', 'is_visible')

    def perform_create(self, serializer):
        """Assign academic year and audit fields on creation."""
        current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
        if not current_academic_year:
            raise NotFound("Current academic year not found.")
        
        # ✅ No need to call is_valid() again here
        serializer.save(
            academic_year=current_academic_year,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        """Update audit fields on modification."""
        # ✅ No is_valid() call here either
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
    search_fields = [
        'subject__name',
        'exam__name',
        'exam__exam_type__name',
    ]
    filterset_fields = [
        'subject',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_skills',
        'has_subject_co_scholastic_grade'
    ]
    ordering_fields = [
        'date',
        'exam_start_time',
        'exam_end_time',
        'subject__name',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_skills',
    ]
    pagination_class = CustomPagination
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    # ✅ Get exam_id from URL kwargs
    def get_exam_id(self):
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

    # ✅ No need to revalidate serializer here
    def perform_create(self, serializer):
        exam_id = self.get_exam_id()
        exam = get_object_or_404(Exam, pk=exam_id)
        serializer.save(
            exam=exam,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        exam_id = self.get_exam_id()
        exam = get_object_or_404(Exam, pk=exam_id)
        serializer.save(
            exam=exam,
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
    http_method_names = ['get', 'post', 'put']
    filter_backends = [DjangoFilterBackend, SearchFilter]

    search_fields = [
        'subject_skill__name',              # search by skill name
        'subject_skill__subject__name',     # search by related subject name
    ]

    filterset_fields = [
        'subject_skill',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_co_scholastic_grade',
        'subject_skill__name',
        'subject_skill__subject__name',
    ]

    ordering_fields = [
        'subject_skill__subject__name',
        'subject_skill__name',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_co_scholastic_grade',
    ]

    pagination_class = CustomPagination
    lookup_field = 'pk'
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
            exam_instance_id=exam_instance_id,  # ✅ direct FK reference
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

    filterset_fields = [
        'academic_year',
        'branch',
        'exam',
        'status',
        'is_visible',
        'is_active',
    ]

    ordering_fields = [
        'academic_year__name',
        'branch__name',
        'exam__name',
        'status__name',
        'marks_entry_expiry_datetime',
        'marks_completion_percentage',
        'updated_at',
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
        'section__name',
        'section__class_name__name',     
        'section__orientation__name',     
        'status__name',
    ]

    filterset_fields = [
        'academic_year',
        'section__name',
        'section__class_name',         
        'section__orientation',           
        'status',
        'is_visible',
        'is_active',
    ]

    ordering_fields = [
        'academic_year__name',
        'section__name',
        'section__class_name__name',     
        'section__orientation__name',     
        'status__name',
        'marks_entry_expiry_datetime',
        'marks_completion_percentage',
        'updated_at',
    ]


    def get_queryset(self):
        """
        Filters queryset by branch_id and exam_id passed in the URL.
        """
        branch_id = self.kwargs.get('branch_id')
        exam_id = self.kwargs.get('exam_id')

        if not branch_id:
            return Response({'branch_id': "This field is required in the URL."}, status=status.HTTP_400_BAD_REQUEST)
        if not exam_id:
            return Response({'exam_id': "This field is required in the URL."}, status=status.HTTP_400_BAD_REQUEST)
        
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
def update_section_wise_exam_result_status_view(request):
    """
    Syncs section-wise exam result status from branch-wise exam result status
    for a given branch and exam.
    - Updates existing records.
    - Creates missing SectionWiseExamResultStatus records if not found.
    """
    branch_wise_exam_result_status_id = request.query_params.get('branch_wise_exam_result_status_id')
    if not branch_wise_exam_result_status_id:
        return Response({'branch_wise_exam_result_status_id': "This field is required in the URL."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get branch-wise record
    branch_status = BranchWiseExamResultStatus.objects.select_related('branch', 'exam', 'academic_year').filter(
        id=branch_wise_exam_result_status_id,
        is_active=True
    ).first()
    if not branch_status:
        return Response({'branch_wise_exam_result_status_id': "Invalid Branch Wise Exam Result Status ID."}, status=status.HTTP_400_BAD_REQUEST)
   
    if not branch_status.academic_year:
        return Response({'academic_year': "Academic year is missing for this record."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get all matching sections
    sections = Section.objects.filter(
        academic_year=branch_status.academic_year,
        branch=branch_status.branch,
        class_name__class_name_id__in=branch_status.exam.student_classes.values_list('class_name_id', flat=True),
        orientation__orientation_id__in=branch_status.exam.orientations.values_list('orientation_id', flat=True),
        is_active=True,
        has_students=True,
    ).distinct()

    if not sections.exists():
        return Response({
            "success": False,
            "message": "No sections found matching the given branch, exam classes, and orientations."
        }, status=status.HTTP_404_NOT_FOUND)

    # ✅ Bulk update existing records
    existing_records = SectionWiseExamResultStatus.objects.filter(
        section__in=sections,
        branch=branch_status.branch,
        exam=branch_status.exam,
        is_active=True,
        academic_year=branch_status.academic_year
    )

    updated_count = existing_records.update(
        is_progress_card_downloaded=branch_status.is_progress_card_downloaded,
        marks_entry_expiry_datetime=branch_status.marks_entry_expiry_datetime,
        is_visible=branch_status.is_visible,
        updated_at=timezone.now()
    )

    # ✅ Identify and create missing records
    existing_section_ids = existing_records.values_list('section__section_id', flat=True)
    missing_sections = sections.exclude(section_id__in=existing_section_ids)

    created_count = 0
    if missing_sections.exists():
        new_objects = [
            SectionWiseExamResultStatus(
                academic_year=branch_status.academic_year,
                branch=branch_status.branch,
                section=section,
                exam=branch_status.exam,
                marks_entry_expiry_datetime=branch_status.marks_entry_expiry_datetime,
                is_visible=branch_status.is_visible,
                is_progress_card_downloaded=branch_status.is_progress_card_downloaded,
                is_active=True,
            )
            for section in missing_sections
        ]
        SectionWiseExamResultStatus.objects.bulk_create(new_objects)
        created_count = len(new_objects)

    # ✅ Response
    if updated_count == 0 and created_count == 0:
        msg = "All section-wise exam result statuses are already up to date."
    else:
        msg = f"{updated_count} section-wise records updated, {created_count} created successfully."

    return Response({
        "success": True,
        "message": msg,
        "branch": branch_status.branch.name,
        "exam": branch_status.exam.name,
        "academic_year": branch_status.academic_year.name
    }, status=status.HTTP_200_OK)



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

# from django.utils import timezone
# from django.db import transaction
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from .models import Exam, BranchWiseExamResultStatus


class PublishProgressCardAPIView(APIView):
 
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        exam_id = request.query_params.get("exam_id")

        # ✅ Validate exam_id
        if not exam_id:
            return Response({"detail": "exam_id is required."},status=status.HTTP_400_BAD_REQUEST,)

        # ✅ Get exam
        try:
            exam = Exam.objects.get(exam_id=exam_id)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found."},status=status.HTTP_404_NOT_FOUND,)

        # ✅ Check if exam is expired
        # now = timezone.now()
        # if exam.marks_entry_expiry_datetime and exam.marks_entry_expiry_datetime < now:
        #     return Response(
        #         {"message": "Cannot publish progress card. Exam has expired."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # ✅ Update exam visibility fields
        exam.is_progress_card_visible = True
        exam.updated_by = request.user
        exam.is_editable  = False
        exam.save(update_fields=["is_progress_card_visible","is_editable", "updated_by"])

        # ✅ Optionally, you can also mark all BranchWiseExamResultStatus as progress card visible
        # (only if you maintain a similar field there)
        branch_updated_count = 0
        with transaction.atomic():
            branches = BranchWiseExamResultStatus.objects.filter(exam=exam)
            for branch in branches:
                branch.is_progress_card_downloaded = True  # 👈 optional — use your field name
            BranchWiseExamResultStatus.objects.bulk_update(
                branches, ["is_progress_card_downloaded"]
            )
            branch_updated_count = branches.count()

        return Response(
            {
                "message": f"Progress card published for exam '{exam.name}'.",
                "branches_updated": branch_updated_count,
            },
            status=status.HTTP_200_OK,
        )
#=============================================================================================================
#============================================ Marks Entry Page ===============================================
#=============================================================================================================
@api_view(['GET'])
@permission_classes([CanViewExamResult, CanAddExamResult])
def create_exam_results(request):
    section_status_id = request.query_params.get('section_wise_exam_result_status_id')
    if not section_status_id:
        return Response({'section_wise_exam_result_status_id': "This field is required in the URL."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        section_status = SectionWiseExamResultStatus.objects.select_related('exam', 'section').get(
            id=section_status_id, is_active=True
        )
    except SectionWiseExamResultStatus.DoesNotExist:
        return Response({'section_wise_exam_result_status_id': "Invalid id"},
                        status=status.HTTP_400_BAD_REQUEST)

    exam = section_status.exam
    exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True) #.select_related('subject')
    students = Student.objects.filter(
        section=section_status.section,
        is_active=True,
        academic_year=exam.academic_year,
    ).exclude(admission_status__admission_status_id=3,)

    existing_results = ExamResult.objects.filter(
        student__in=students,
        exam_instance__in=exam_instances,
        is_active=True
    ).select_related('student', 'exam_instance', 'exam_attendance', 'co_scholastic_grade')

    results_dict = {(res.student_id, res.exam_instance_id): res for res in existing_results}

    # Create missing ExamResults
    new_results = []
    for instance in exam_instances:
        for student in students:
            key = (student.student_id, instance.exam_instance_id)
            if key not in results_dict:
                new_result = ExamResult.objects.create(student=student, exam_instance=instance)
                results_dict[key] = new_result
                new_results.append(new_result)

    # Handle skill results
    for instance in exam_instances.filter(has_subject_skills=True):
        skills = instance.subject_skills.all()
        for student in students:
            res = results_dict.get((student.student_id, instance.exam_instance_id))
            for skill in skills:
                ExamSkillResult.objects.get_or_create(exam_result=res, skill=skill)

    # Build response
    data = []
    for student in students:
        student_dict = {
            'student_id': student.student_id,
            'student_name': student.name,
            'SCS_Number': student.SCS_Number,
            'exam_instances': []
        }

        # Build response
        for instance in exam_instances:
            res = results_dict.get((student.student_id, instance.exam_instance_id))
            skills_data = []
            if instance.has_subject_skills:
                for skill in instance.subject_skills.all():
                    skill_instance = ExamSubjectSkillInstance.objects.filter(
                        exam_instance=instance, subject_skill=skill, is_active=True
                    ).first()

                    skill_result = ExamSkillResult.objects.filter(
                        exam_result=res, skill=skill
                    ).first()

                    skills_data.append({
                        'skill_name': skill.name,
                        'has_external_marks': skill_instance.has_external_marks if skill_instance else False,
                        'has_internal_marks': skill_instance.has_internal_marks if skill_instance else False,
                        'has_subject_co_scholastic_grade': skill_instance.has_subject_co_scholastic_grade if skill_instance else False,
                        'exam_skill_result_id': skill_result.exam_skill_result_id if skill_result else None,
                        'max_cut_off_marks_external' : skill_instance.cut_off_marks_external if skill_instance else 0,
                        'external_marks': skill_result.external_marks if skill_result else None,
                        'max_cut_off_marks_internal': skill_instance.cut_off_marks_internal if skill_instance else 0,
                        'internal_marks': skill_result.internal_marks if skill_result else None,
                        'co_scholastic_grade': skill_result.co_scholastic_grade.id if skill_result and skill_result.co_scholastic_grade else None,
                    })

            student_dict['exam_instances'].append({
                'subject_name': instance.subject.name,
                'exam_result_id': res.exam_result_id if res else None,
                'has_external_marks': instance.has_external_marks,
                'has_internal_marks': instance.has_internal_marks,
                'has_subject_co_scholastic_grade': instance.has_subject_co_scholastic_grade,
                'exam_attendance': res.exam_attendance.exam_attendance_status_id if res and res.exam_attendance else None,
                'max_cut_off_marks_external': instance.cut_off_marks_external,
                'external_marks': res.external_marks if res else None,
                'max_cut_off_marks_internal': instance.cut_off_marks_internal,
                'internal_marks': res.internal_marks if res else None,
                'co_scholastic_grade': res.co_scholastic_grade.id if res and res.co_scholastic_grade else None,
                'has_subject_skills': instance.has_subject_skills,
                'exam_skill_instances': skills_data,
            })

        data.append(student_dict)

    return Response(data)



# @api_view(['GET'])
# @api_view([CanViewExamResult])
# def create_exam_results(request):
#     section_wise_exam_result_status_id = request.query_params.get('section_wise_exam_result_status_id')
#     if not section_wise_exam_result_status_id:
#         return Response({'section_wise_exam_result_status_id': "This field is required in the URL."}, status=status.HTTP_400_BAD_REQUEST)
    
#     section_wise_exam_result_status = SectionWiseExamResultStatus.objects.get(id=section_wise_exam_result_status_id, is_active=True)
#     if not section_wise_exam_result_status:
#         return Response({'section_wise_exam_result_status_id': "Invalid id"}, status=status.HTTP_400_BAD_REQUEST)
    
#     exam = section_wise_exam_result_status.exam
#     exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True)
#     students = Student.objects.filter(section=section_wise_exam_result_status.section, is_active=True, admission_status__admission_status_id=3)  # admission_status_id for Dropout Students
    
#     for instance in exam_instances:
#         existing_students = ExamResult.objects.filter(student__student_id__in=students.values_list('student_id', flat=True).distinct(), exam_instance=instance, is_active=True)
#         missing_students = students.exclude(student_id=existing_students.values_list('student__students_id', flat=True))

#         if missing_students.exists():
#             new_results = [
#                 ExamResult(
#                     student=student,
#                     exam_instance = instance,
#                 )
#                 for student in missing_students
#             ]
#             ExamResult.objects.bulk_create(new_results)

#     # exam_results = ExamResult.objects.filter(student__student_id__in=students.values_list('student_id', flat=True).distinct(), exam_instance__exam_instance_id__in=exam_instances.values_list('exam_instance_id', flat=True), is_active=True)

#     data = []

#     for student in students:
#         for instance in exam_instances:
#             # student_result = exam_results.filter(student=student, exam_instance=instance)
#             student_result = ExamResult.objects.filter(student=student, exam_instance=instance)
#             student_data = {
#                 'student_name' : student.name,
#                 'SCS_Number' : student.SCS_Number,
                
#                 'exam_instances' :{
#                     'subject_name' : instance.subject.name,
#                     'has_external_marks' : instance.has_external_marks,
#                     'has_internal_marks' : instance.has_internal_marks,
#                     'has_subject_co_scholastic_grade' : instance.has_subject_co_scholastic_grade,
#                     'exam_result_id': student_result.exam_result_id,
#                     'exam_attendance' : student_result.exam_attendance,
#                     'external_marks': student_result.external_marks,
#                     'internal_marks': student_result.internal_marks,
#                     'co_scholastic_grade': student_result.co_scholastic_grade,

#                     'has_subject_skills' : instance.has_subject_skills,
#                 }
#             }

#             data.append(student_data)

#     return Response(data)

# class EditExamResults(ModelViewSet):
#     permission_classes = [CanChangeExamResult]
#     serializer_class = 
#     http_method_names = ['get', 'put']

#     def get_queryset(self):
#         return 



