from django.contrib import admin
from .models import *

# ===================== Subject =====================

@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('-id',)
    list_editable = ('is_active',)
    list_per_page = 25


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'display_name', 'created_at', 'updated_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'display_name', 'description', 'category__name')
    autocomplete_fields = ('category', 'academic_devisions', 'class_names')
    list_editable = ('is_active',)
    list_per_page = 25


@admin.register(SubjectSkill)
class SubjectSkillAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'subject', 'is_active')
    search_fields = ('name', 'subject__name')
    list_filter = ('is_active',)
    autocomplete_fields = ('subject',)


# ===================== Exam Type =====================
@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('exam_type_id','name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(ExamCategory)
class ExamCategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('-id',)


# ===================== Exam =====================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_id','name', 'exam_type', 'category','is_active','exam_status', 'is_visible', 'is_editable' ,'is_progress_card_visible')
    search_fields = ('name', 'exam_type__name', 'exam_status__name', 'category__name')
    list_filter = ('is_active','exam_status', 'exam_type', 'category','is_editable', 'is_visible', 'is_progress_card_visible')
    filter_horizontal = ('states', 'zones', 'branches', 'orientations', 'academic_devisions', 'student_classes')
    autocomplete_fields = ('exam_type',)
    ordering = ('-exam_id',)


# ===================== Exam Instance =====================
@admin.register(ExamInstance)
class ExamInstanceAdmin(admin.ModelAdmin):
    list_display = ('exam_instance_id', 'exam', 'subject', 'sequence', 'date', 'is_optional', 'is_active')
    search_fields = ('exam__name', 'subject__name')
    list_filter = ('is_active', 'is_optional', 'has_external_marks', 'has_internal_marks', 'has_subject_skills', 'has_subject_co_scholastic_grade')
    filter_horizontal = ('subject_skills',)
    autocomplete_fields = ('exam', 'subject')


# ===================== Exam Subject Skill Instance =====================
@admin.register(ExamSubjectSkillInstance)
class ExamSubjectSkillInstanceAdmin(admin.ModelAdmin):
    list_display = ('id','exam_instance', 'subject_skill', 'is_active')
    list_filter = ('is_active', 'has_external_marks', 'has_internal_marks', 'has_subject_co_scholastic_grade')
    autocomplete_fields = ('exam_instance', 'subject_skill')


# ===================== Exam Attendance Status =====================
@admin.register(ExamAttendanceStatus)
class ExamAttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('exam_attendance_status_id','name', 'short_code', 'is_active')
    search_fields = ('name', 'short_code')
    list_filter = ('is_active',)


# ===================== Grade Boundary =====================
from django.contrib import admin
from .models import GradeBoundary


@admin.register(GradeBoundary)
class GradeBoundaryAdmin(admin.ModelAdmin):
    list_display = (
        'grade',
        'category',
        'min_percentage',
        'max_percentage',
        'remarks',
        'is_active',
    )
    list_filter = ('is_active', 'category')
    search_fields = ('grade', 'remarks', 'category__name')
    ordering = ( 'category','-min_percentage',)
    list_editable = ('is_active',)
    list_per_page = 20

    fieldsets = (
        ('Grade Information', {
            'fields': ('grade', 'category','remarks')
        }),
        ('Percentage Range', {
            'fields': ('min_percentage', 'max_percentage')
        }),
        ('Status', {
            'fields': ('is_active',) 
        }),
    )


# ===================== Co-Scholastic Grade =====================
@admin.register(CoScholasticGrade)
class CoScholasticGradeAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'category','description', 'point', 'is_active')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('is_active',)
    ordering = ( 'category',)


# ===================== Exam Result =====================
@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('exam_result_id','student', 'exam_instance', 'total_marks', 'percentage', 'is_active')
    search_fields = ('student__name', 'exam_instance__subject__name', 'exam_instance__exam__name')
    list_filter = ('is_active',)
    autocomplete_fields = ('student', 'exam_instance', 'exam_attendance', 'co_scholastic_grade')


# ===================== Exam Skill Result =====================
@admin.register(ExamSkillResult)
class ExamSkillResultAdmin(admin.ModelAdmin):
    list_display = ('exam_skill_result_id', 'exam_result', 'skill', 'marks_obtained')
    search_fields = ('exam_result__student__name', 'skill__name')
    list_filter = ()
    autocomplete_fields = ('exam_result', 'skill', 'co_scholastic_grade')


# ===================== Student Exam Summary =====================
from django.contrib import admin
from .models import StudentExamSummary


@admin.register(StudentExamSummary)
class StudentExamSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "students_exam_summary_id",
        "student",
        "exam",
        "subjects_percentage",
        "subject_grade",
        "skills_percentage",
        "skills_grade",
        "section_rank",
        "class_rank",
        "state_rank",
        "all_india_rank",
        "is_active",
    )

    list_filter = (
        "exam",
        "subject_grade",
        "skills_grade",
        "is_active",
    )

    search_fields = (
        "student__name",
        "student__SCS_Number",
        "exam__name",
    )

    autocomplete_fields = (
        "student",
        "exam",
        "subject_grade",
        "skills_grade",
    )

    ordering = ("-students_exam_summary_id",)
    list_per_page = 25


# ==================== ExamResultStatus ====================
@admin.register(ExamResultStatus)
class ExamResultStatusAdmin(admin.ModelAdmin):
    list_display = ('id',"name", "description", "display_order")
    search_fields = ("name", "description")
    ordering = ("display_order", "name")


# ==================== BranchWiseExamResultStatus ====================
@admin.register(BranchWiseExamResultStatus)
class BranchWiseExamResultStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "academic_year",
        "branch",
        "exam",
        "status",
        "marks_completion_percentage",
        "is_progress_card_downloaded",
        "is_visible",
        "is_active",
        "finalized_by",
        "finalized_at",
    )
    list_filter = (
        "academic_year",
        "branch",
        "exam",
        "status",
        "is_visible",
        "is_active",
    )
    search_fields = (
        "exam__name",
        "branch__name",
        "academic_year__name",
        "status__name",
    )
    ordering = ("academic_year", "branch", "exam")

    # ✅ Optimize foreign key lookups
    autocomplete_fields = (
        "academic_year",
        "branch",
        "exam",
        "status",
        "finalized_by",
    )

    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Basic Information", {
            "fields": ("academic_year", "branch", "exam", "status"),
        }),
        ("Progress & Completion", {
            "fields": (
                "marks_completion_percentage",
                "marks_entry_expiry_datetime",
                "is_progress_card_downloaded",
                "total_sections",
                "number_of_sections_completed",
                "number_of_sections_pending",
                "progress_card_pending_sections",
            ),
        }),
        ("Finalization", {
            "fields": ("finalized_by", "finalized_at"),
        }),
        ("Visibility & Status", {
            "fields": ("is_visible", "is_active", "updated_at"),
        }),
    )


# ==================== SectionWiseExamResultStatus ====================
@admin.register(SectionWiseExamResultStatus)
class SectionWiseExamResultStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "academic_year",
        "branch",
        "section",
        "exam",
        "status",
        "marks_completion_percentage",
        "is_progress_card_downloaded",
        "is_visible",
        "is_active",
        "finalized_by",
        "finalized_at",
    )
    list_filter = (
        "academic_year",
        "branch",
        "section",
        "exam",
        "status",
        "is_visible",
        "is_active",
    )
    search_fields = (
        "exam__name",
        "section__name",
        "branch__name",
        "academic_year__name",
        "status__name",
    )
    ordering = ("academic_year", "branch", "section", "exam")

    # ✅ Optimize foreign key lookups
    autocomplete_fields = (
        "academic_year",
        "branch",
        "section",
        "exam",
        "status",
        "finalized_by",
    )

    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Basic Information", {
            "fields": ("academic_year", "branch", "section", "exam", "status"),
        }),
        ("Progress & Completion", {
            "fields": (
                "marks_completion_percentage",
                "marks_entry_expiry_datetime",
                "is_progress_card_downloaded",
            ),
        }),
        ("Finalization", {
            "fields": ("finalized_by", "finalized_at"),
        }),
        ("Visibility & Status", {
            "fields": ("is_visible", "is_active", "updated_at"),
        }),
    )


@admin.register(ExamStatus)
class ExamStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('id',)