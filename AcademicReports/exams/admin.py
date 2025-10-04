from django.contrib import admin
from .models import (
    Subject, SubjectSkill, ExamType, Exam, ExamInstance,
    ExamAttendanceStatus, GradeBoundary, ExamResult,
    ExamSkillResult, StudentExamSummary
)

# ==================== Subject Admin ====================
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active')
    list_filter = ('is_active', 'academic_devisions', 'class_names')
    search_fields = ('name', 'description', 'display_name')
    filter_horizontal = ('academic_devisions', 'class_names')
    ordering = ('name',)


# ==================== SubjectSkill Admin ====================
@admin.register(SubjectSkill)
class SubjectSkillAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'is_active')
    list_filter = ('is_active', 'subject')
    search_fields = ('name', 'subject__name')
    ordering = ('subject', 'name')


# ==================== ExamType Admin ====================
@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)


# ==================== Exam Admin ====================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'academic_year', 'start_date', 'end_date', 'is_visible', 'is_active')
    list_filter = (
        'exam_type', 'academic_year', 'states', 'zones', 'branches',
        'orientations', 'academic_devisions', 'student_classes',
        'is_visible', 'is_active'
    )
    search_fields = ('name', 'exam_type__name', 'academic_year__name')
    filter_horizontal = ('states', 'zones', 'branches', 'orientations', 'academic_devisions', 'student_classes')
    ordering = ('-start_date', 'name')


# ==================== ExamInstance Admin ====================
@admin.register(ExamInstance)
class ExamInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'exam', 'subject', 'date', 'exam_start_time', 'exam_end_time',
        'has_external_marks', 'has_internal_marks', 'has_subject_skills',
        'is_optional', 'is_active'
    )
    list_filter = ('exam', 'subject', 'has_external_marks', 'has_internal_marks', 'has_subject_skills', 'is_optional', 'is_active')
    search_fields = ('exam__name', 'subject__name')
    filter_horizontal = ('subject_skills',)
    ordering = ('exam', 'date')


# ==================== ExamAttendanceStatus Admin ====================
@admin.register(ExamAttendanceStatus)
class ExamAttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'short_code', 'description')
    ordering = ('name',)


# ==================== GradeBoundary Admin ====================
@admin.register(GradeBoundary)
class GradeBoundaryAdmin(admin.ModelAdmin):
    list_display = ('grade', 'exam_type', 'orientation', 'min_percentage', 'max_percentage', 'is_active')
    list_filter = ('exam_type', 'orientation', 'is_active')
    search_fields = ('grade', 'exam_type__name', 'orientation__name')
    ordering = ('-min_percentage',)


# ==================== ExamResult Admin ====================
@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'exam_instance', 'exam_attendance',
        'external_marks', 'internal_marks', 'marks_obtained', 'percentage',
        'class_rank', 'section_rank', 'zone_rank', 'state_rank', 'all_india_rank',
        'is_active'
    )
    list_filter = ('exam_instance', 'exam_attendance', 'is_active')
    search_fields = ('student__name', 'student__SCS_Number', 'exam_instance__exam__name', 'exam_instance__subject__name')
    ordering = ('student', 'exam_instance')


# ==================== ExamSkillResult Admin ====================
@admin.register(ExamSkillResult)
class ExamSkillResultAdmin(admin.ModelAdmin):
    list_display = ('exam_result', 'skill', 'grade')
    list_filter = ('skill',)
    search_fields = ('exam_result__student__name', 'exam_result__student__SCS_Number', 'skill__name')
    ordering = ('exam_result', 'skill')


# ==================== StudentExamSummary Admin ====================
@admin.register(StudentExamSummary)
class StudentExamSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'exam', 'total_subjects_marks', 'percentage',
        'overall_grade', 'overall_remarks',
        'section_rank', 'class_rank', 'zone_rank', 'state_rank', 'all_india_rank',
        'is_active'
    )
    list_filter = ('exam', 'is_active')
    search_fields = ('student__name', 'student__SCS_Number', 'exam__name')
    ordering = ('student', 'exam')
