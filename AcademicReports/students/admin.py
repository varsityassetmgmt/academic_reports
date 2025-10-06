from django.contrib import admin
from .models import *


# ==================== ClassName Admin ====================
@admin.register(ClassName)
class ClassNameAdmin(admin.ModelAdmin):
    list_display = ('class_name_id', 'name', 'class_sequence', 'varna_class_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'varna_class_id')
    ordering = ('class_sequence', 'name')


# ==================== Orientation Admin ====================
@admin.register(Orientation)
class OrientationAdmin(admin.ModelAdmin):
    list_display = ('orientation_id','name', 'short_code', 'varna_orientation_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'short_code', 'description', 'varna_orientation_id')
    ordering = ('name',)


# ==================== Gender Admin ====================
@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('gender_id','name', 'varna_gender_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'varna_gender_id')
    ordering = ('name',)


# ==================== AdmissionStatus Admin ====================
@admin.register(AdmissionStatus)
class AdmissionStatusAdmin(admin.ModelAdmin):
    list_display = ('admission_status_id','admission_status', 'short_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('admission_status', 'short_code')
    ordering = ('admission_status',)


# ==================== Student Admin ====================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id',
        'SCS_Number', 'name', 'academic_year', 'branch', 'zone', 'state',
        'student_class', 'section', 'gender', 'admission_status',
        'orientation', 'is_active'
    )
    list_filter = (
        'academic_year', 'state', 'zone', 'branch',
        'student_class', 'section', 'gender', 'admission_status', 'orientation', 'is_active'
    )
    search_fields = ('SCS_Number', 'name', 'varna_student_id')
    ordering = ('name', 'SCS_Number')
    list_select_related = (
        'academic_year', 'state', 'zone', 'branch',
        'student_class', 'section', 'gender', 'admission_status', 'orientation'
    )

@admin.register(BranchOrientations)
class BranchOrientationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'academic_year', 'get_orientations', 'is_active')
    list_filter = ('academic_year', 'branch__state', 'branch__zone', 'is_active')
    search_fields = ('branch__name', 'academic_year__name', 'orientations__name')
    filter_horizontal = ('orientations',)
    ordering = ('branch__name',)

    def get_orientations(self, obj):
        """Display orientations as comma-separated values."""
        return ", ".join(o.name for o in obj.orientations.all())
    get_orientations.short_description = 'Orientations'
