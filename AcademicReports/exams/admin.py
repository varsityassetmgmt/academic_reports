from django.contrib import admin
from .models import *

# ===================== Subject =====================
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active')
    search_fields = ('name', 'display_name')
    list_filter = ('is_active',)
    filter_horizontal = ('academic_devisions', 'class_names')


@admin.register(SubjectSkill)
class SubjectSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'is_active')
    search_fields = ('name', 'subject__name')
    list_filter = ('is_active',)
    autocomplete_fields = ('subject',)


# ===================== Exam Type =====================
@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


# ===================== Exam =====================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'is_active', 'is_visible', 'is_progress_card_visible')
    search_fields = ('name', 'exam_type__name')
    list_filter = ('is_active', 'is_visible', 'is_progress_card_visible')
    filter_horizontal = ('states', 'zones', 'branches', 'orientations', 'academic_devisions', 'student_classes')
    autocomplete_fields = ('exam_type',)


# ===================== Exam Instance =====================
@admin.register(ExamInstance)
class ExamInstanceAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'date', 'is_optional', 'is_active')
    search_fields = ('exam__name', 'subject__name')
    list_filter = ('is_active', 'is_optional', 'has_external_marks', 'has_internal_marks', 'has_subject_skills', 'has_subject_co_scholastic_grade')
    filter_horizontal = ('subject_skills',)
    autocomplete_fields = ('exam', 'subject')


# ===================== Exam Subject Skill Instance =====================
@admin.register(ExamSubjectSkillInstance)
class ExamSubjectSkillInstanceAdmin(admin.ModelAdmin):
    list_display = ('exam_instance', 'subject_skill', 'is_active')
    list_filter = ('is_active', 'has_external_marks', 'has_internal_marks', 'has_subject_co_scholastic_grade')
    autocomplete_fields = ('exam_instance', 'subject_skill')


# ===================== Exam Attendance Status =====================
@admin.register(ExamAttendanceStatus)
class ExamAttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_code', 'is_active')
    search_fields = ('name', 'short_code')
    list_filter = ('is_active',)


# ===================== Grade Boundary =====================
@admin.register(GradeBoundary)
class GradeBoundaryAdmin(admin.ModelAdmin):
    list_display = ('grade', 'exam_type', 'orientation', 'min_percentage', 'max_percentage', 'is_active')
    search_fields = ('grade', 'exam_type__name', 'orientation__name')
    list_filter = ('is_active',)
    autocomplete_fields = ('exam_type', 'orientation')


# ===================== Co-Scholastic Grade =====================
@admin.register(CoScholasticGrade)
class CoScholasticGradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'point', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)


# ===================== Exam Result =====================
@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam_instance', 'total_marks', 'percentage', 'is_active')
    search_fields = ('student__name', 'exam_instance__subject__name', 'exam_instance__exam__name')
    list_filter = ('is_active',)
    autocomplete_fields = ('student', 'exam_instance', 'exam_attendance', 'co_scholastic_grade')


# ===================== Exam Skill Result =====================
@admin.register(ExamSkillResult)
class ExamSkillResultAdmin(admin.ModelAdmin):
    list_display = ('exam_result', 'skill', 'marks_obtained')
    search_fields = ('exam_result__student__name', 'skill__name')
    list_filter = ()
    autocomplete_fields = ('exam_result', 'skill', 'co_scholastic_grade')


# ===================== Student Exam Summary =====================
@admin.register(StudentExamSummary)
class StudentExamSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'total_subjects_marks', 'percentage', 'overall_grade', 'is_active')
    search_fields = ('student__name', 'exam__name')
    list_filter = ('is_active',)
    autocomplete_fields = ('student', 'exam')


from django.contrib import admin
from .models import ExamResultStatus, BranchWiseExamResultStatus, SectionWiseExamResultStatus


# ==================== ExamResultStatus ====================
@admin.register(ExamResultStatus)
class ExamResultStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "display_order")
    search_fields = ("name", "description")
    ordering = ("display_order", "name")


# ==================== BranchWiseExamResultStatus ====================
@admin.register(BranchWiseExamResultStatus)
class BranchWiseExamResultStatusAdmin(admin.ModelAdmin):
    list_display = (
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
