from django.contrib import admin
from .models import *

# ==================== AcademicYear Admin ====================
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('academic_year_id','name', 'start_date', 'end_date', 'is_current_academic_year', 'is_active')
    list_filter = ('is_current_academic_year', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('-start_date',)

# ==================== AcademicDevision Admin ====================
@admin.register(AcademicDevision)
class AcademicDevisionAdmin(admin.ModelAdmin):
    list_display = ('academic_devision_id','name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    filter_horizontal = ('classes',)  # Many-to-many field for easier selection

# ==================== State Admin ====================
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('state_id','name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

# ==================== Zone Admin ====================
@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_id','name', 'state', 'is_active')
    list_filter = ('state', 'is_active')
    search_fields = ('name', 'state__name')

# ==================== Branch Admin ====================
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_id','name', 'state', 'zone', 'city', 'is_active', 'created_at', 'updated_at')
    list_filter = ('state', 'zone', 'is_active')
    search_fields = ('name', 'building_code', 'location_incharge', 'city', 'address')
    filter_horizontal = ('academic_devisions', 'classes', 'orientations')  # Many-to-many fields
    ordering = ('name',)
