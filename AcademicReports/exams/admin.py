from django.contrib import admin
from .models import *

# ==================== Subject Admin ====================
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id','name', 'display_name', 'is_active')
    list_filter = ('is_active', 'academic_devisions', 'class_names')
    search_fields = ('name', 'description', 'display_name')
    filter_horizontal = ('academic_devisions', 'class_names')
    ordering = ('name',)


# ==================== SubjectSkill Admin ====================
@admin.register(SubjectSkill)
class SubjectSkillAdmin(admin.ModelAdmin):
    list_display = ('id','subject', 'name', 'is_active')
    list_filter = ('is_active', 'subject')
    search_fields = ('name', 'subject__name')
    ordering = ('subject', 'name')


# ==================== ExamType Admin ====================
@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('exam_type_id','name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)


# ==================== Exam Admin ====================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    # ================= Display Setup =================
    list_display = (
        'exam_id',
        'name',
        'exam_type',
        'academic_year',
        'start_date',
        'end_date',
        'is_visible',
        'is_progress_card_visible',
        'is_active',
    )
    list_display_links = ('name',)

    # ================= Filters =================
    list_filter = (
        'exam_type',
        'academic_year',
        'states',
        'zones',
        'branches',
        'orientations',
        'academic_devisions',
        'student_classes',
        'is_visible',
        'is_progress_card_visible',
        'is_active',
    )

    # ================= Search =================
    search_fields = (
        'name',
        'exam_type__name',
        'academic_year__name',
    )

    # ================= M2M Field Controls =================
    filter_horizontal = (
        'states',
        'zones',
        'branches',
        'orientations',
        'academic_devisions',
        'student_classes',
    )

    # ================= Ordering =================
    ordering = ('-start_date', 'name')

    # ================= Inline Editing =================
    list_editable = ('is_visible', 'is_progress_card_visible', 'is_active')

    # ================= Optimizations =================
    autocomplete_fields = ('exam_type', 'academic_year')
    list_per_page = 25

    # ================= Field Grouping =================
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'exam_type', 'academic_year', ('start_date', 'end_date'))
        }),
        ('Associations', {
            'fields': (
                'states',
                'zones',
                'branches',
                'orientations',
                'academic_devisions',
                'student_classes',
            ),
            'classes': ('collapse',),  # collapsible for cleaner view
        }),
        ('Visibility and Status', {
            'fields': (
                'is_visible',
                'is_progress_card_visible',
                'is_active',
            ),
        }),
    )

# ==================== ExamInstance Admin ===================

@admin.register(ExamInstance)
class ExamInstanceAdmin(admin.ModelAdmin):
    # ================= Display Setup =================
    list_display = (
        'exam_instance_id',
        'exam',
        'subject',
        'date',
        'exam_start_time',
        'exam_end_time',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_skills',
        'has_subject_co_scholastic_grade',
        'is_optional',
        'is_active',
    )
    list_display_links = ('exam', 'subject')

    # ================= Filters =================
    list_filter = (
        'exam__exam_type',
        'exam',
        'subject',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_skills',
        'has_subject_co_scholastic_grade',
        'is_optional',
        'is_active',
        'date',
    )

    # ================= Search =================
    search_fields = (
        'exam__name',
        'exam__exam_type__name',
        'subject__name',
    )

    # ================= M2M Controls =================
    filter_horizontal = ('subject_skills',)

    # ================= Ordering =================
    ordering = ('-date', 'exam', 'subject')

    # ================= Inline Editing =================
    list_editable = (
        'has_external_marks',
        'has_internal_marks',
        'has_subject_skills',
        'has_subject_co_scholastic_grade',
        'is_optional',
        'is_active',
    )

    # ================= Performance Optimizations =================
    autocomplete_fields = ('exam', 'subject')
    list_per_page = 25

    # ================= Field Grouping =================
    fieldsets = (
        ('Exam & Subject', {
            'fields': ('exam', 'subject')
        }),
        ('Date & Time', {
            'fields': ('date', ('exam_start_time', 'exam_end_time'))
        }),
        ('Marks Configuration', {
            'fields': (
                'has_external_marks',
                'maximum_marks_external',
                'cut_off_marks_external',
                'has_internal_marks',
                'maximum_marks_internal',
                'cut_off_marks_internal',
            ),
            'classes': ('collapse',),  # collapsible section
        }),
        ('Skills & Grading', {
            'fields': (
                'has_subject_skills',
                'has_subject_co_scholastic_grade',
                'subject_skills',
            ),
            'classes': ('collapse',),
        }),
        ('Other Settings', {
            'fields': ('is_optional', 'is_active'),
        }),
    )



# ==================== ExamAttendanceStatus Admin ====================
@admin.register(ExamAttendanceStatus)
class ExamAttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('exam_attendance_status_id','name', 'short_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'short_code', 'description')
    ordering = ('name',)


# ==================== GradeBoundary Admin ====================
@admin.register(GradeBoundary)
class GradeBoundaryAdmin(admin.ModelAdmin):
    list_display = ('grade_boundary_id','grade', 'exam_type', 'orientation', 'min_percentage', 'max_percentage', 'is_active')
    list_filter = ('exam_type', 'orientation', 'is_active')
    search_fields = ('grade', 'exam_type__name', 'orientation__name')
    ordering = ('-min_percentage',)


from django.contrib import admin
from .models import ExamResult


# ==================== ExamResult Admin ====================
@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = (
        'exam_result_id',
        'student',
        'exam_instance',
        'exam_attendance',
        'external_marks',
        'internal_marks',
        'total_marks',
        'percentage',
        'class_rank',
        'section_rank',
        'zone_rank',
        'state_rank',
        'all_india_rank',
        'is_active',
    )

    list_filter = (
        'exam_instance',
        'exam_attendance',
        'is_active',
    )

    search_fields = (
        'student__name',
        'student__SCS_Number',
        'exam_instance__exam__name',
        'exam_instance__subject__name',
    )

    ordering = ('student', 'exam_instance')

    # Make certain fields read-only in admin to avoid accidental overwrites
    readonly_fields = (
        'total_marks',
        'percentage',
        'class_rank',
        'section_rank',
        'zone_rank',
        'state_rank',
        'all_india_rank',
    )

    # Improves admin performance with large datasets
    list_select_related = (
        'student',
        'exam_instance',
        'exam_attendance',
    )

    # Optional: Adds field grouping for clarity
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'student',
                'exam_instance',
                'exam_attendance',
                'is_active',
            )
        }),
        ('Marks Details', {
            'fields': (
                'external_marks',
                'internal_marks',
                'total_marks',
                'percentage',
                'co_scholastic_grade',
                'skill_external_marks',
                'skill_internal_marks',
                'skill_total_marks',
            )
        }),
        ('Rank Details', {
            'fields': (
                'class_rank',
                'section_rank',
                'zone_rank',
                'state_rank',
                'all_india_rank',
            )
        }),
    )


# ==================== ExamSkillResult Admin ====================
@admin.register(ExamSkillResult)
class ExamSkillResultAdmin(admin.ModelAdmin):
    # Display fields in admin list view
    list_display = (
        'examp_skill_result_id',
        'exam_result',
        'skill',
        'co_scholastic_grade',
        'external_marks',
        'internal_marks',
        'marks_obtained',
    )

    # Clickable links
    list_display_links = ('exam_result', 'skill')

    # Filters on the right sidebar
    list_filter = (
        'skill',
        'co_scholastic_grade',
    )

    # Searchable fields
    search_fields = (
        'exam_result__student__name',  # assuming ExamResult has student field
        'skill__name',
    )

    # Default ordering
    ordering = ('exam_result', 'skill')

    # Optional: make numeric fields editable inline
    list_editable = (
        'external_marks',
        'internal_marks',
        'marks_obtained',
    )

    # Optimize related lookups
    autocomplete_fields = ('exam_result', 'skill', 'co_scholastic_grade')

    # Optional grouping for better readability
    fieldsets = (
        ('Relations', {
            'fields': ('exam_result', 'skill', 'co_scholastic_grade')
        }),
        ('Marks', {
            'fields': ('external_marks', 'internal_marks', 'marks_obtained')
        }),
    )



# ==================== StudentExamSummary Admin ====================
@admin.register(StudentExamSummary)
class StudentExamSummaryAdmin(admin.ModelAdmin):
    list_display = ('students_exam_summary_id',
        'student', 'exam', 'total_subjects_marks', 'percentage',
        'overall_grade', 'overall_remarks',
        'section_rank', 'class_rank', 'zone_rank', 'state_rank', 'all_india_rank',
        'is_active'
    )
    list_filter = ('exam', 'is_active')
    search_fields = ('student__name', 'student__SCS_Number', 'exam__name')
    ordering = ('student', 'exam')

@admin.register(CoScholasticGrade)
class CoScholasticGradeAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = (
        'name',
        'description',
        'point',
        'is_active',
    )

    # Clickable link fields
    list_display_links = ('name',)

    # Filters on the right-hand side
    list_filter = ('is_active',)

    # Fields searchable via search bar
    search_fields = ('name', 'description')

    # Default ordering
    ordering = ('-point', 'name')

    # Inline editable fields for quick admin updates
    list_editable = ('point', 'is_active')

    # Optional grouping for clarity
    fieldsets = (
        ('Grade Information', {
            'fields': ('name', 'description', 'point')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    # Add a simple style — optional, makes admin easier to read
    list_per_page = 25

# ==================== ExamSubjectSkillInstance Admin ====================
@admin.register(ExamSubjectSkillInstance)
class ExamSubjectSkillInstanceAdmin(admin.ModelAdmin):
    # ================= Display Setup =================
    list_display = (
        'id',
        'exam_instance',
        'subject_skill',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_co_scholastic_grade',
        'maximum_marks_external',
        'cut_off_marks_external',
        'maximum_marks_internal',
        'cut_off_marks_internal',
        'is_active',
    )
    list_display_links = ('exam_instance', 'subject_skill')

    # ================= Filters =================
    list_filter = (
        'exam_instance__exam',
        'exam_instance__subject',
        'subject_skill',
        'has_external_marks',
        'has_internal_marks',
        'has_subject_co_scholastic_grade',
        'is_active',
    )

    # ================= Search =================
    search_fields = (
        'exam_instance__exam__name',
        'exam_instance__subject__name',
        'subject_skill__name',
    )

    # ================= Ordering =================
    ordering = ('exam_instance', 'subject_skill')

    # ================= Inline Editing =================
    list_editable = (
        'has_external_marks',
        'has_internal_marks',
        'has_subject_co_scholastic_grade',
        'is_active',
    )

    # ================= Performance Optimizations =================
    autocomplete_fields = ('exam_instance', 'subject_skill')
    list_select_related = ('exam_instance', 'subject_skill')
    list_per_page = 25

    # ================= Field Grouping =================
    fieldsets = (
        ('Associations', {
            'fields': ('exam_instance', 'subject_skill')
        }),
        ('Configuration Flags', {
            'fields': (
                'has_external_marks',
                'has_internal_marks',
                'has_subject_co_scholastic_grade',
            )
        }),
        ('Marks Setup', {
            'fields': (
                'maximum_marks_external',
                'cut_off_marks_external',
                'maximum_marks_internal',
                'cut_off_marks_internal',
            ),
            'classes': ('collapse',),  # collapsible for cleaner admin UI
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
