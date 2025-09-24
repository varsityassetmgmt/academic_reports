from django.contrib import admin
from .models import ClassName, Orientation

# ==================== ClassName Admin ====================
@admin.register(ClassName)
class ClassNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'varna_class_id', 'class_sequence', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'varna_class_id', 'description')
    ordering = ('class_sequence', 'name')

# ==================== Orientation Admin ====================
@admin.register(Orientation)
class OrientationAdmin(admin.ModelAdmin):
    list_display = ('name', 'varna_orientation_id', 'short_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'varna_orientation_id', 'short_code', 'description')
    ordering = ('name',)
