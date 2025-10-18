from django.contrib import admin
from progresscard.models import *

@admin.register(ExamProgressCardTemplate)
class ExamProgressCardTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    fieldsets = (
        ("Template Details", {
            "fields": ("name", "description", "is_active")
        }),
        ("Template Content", {
            "fields": ("html_template", "css_styles", "script")
        }),
        ("Audit Info", {
            "fields": ("created_by", "updated_by", "created_at", "updated_at")
        }),
    )


@admin.register(ExamProgressCardMapping)
class ExamProgressCardMappingAdmin(admin.ModelAdmin):
    list_display = (
        "exam",
        "template",
        "is_active",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("exam__name", "template__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    autocomplete_fields = ("exam", "template", "created_by", "updated_by")
    fieldsets = (
        ("Mapping Details", {
            "fields": ("exam", "template", "is_active")
        }),
        ("Audit Info", {
            "fields": ("created_by", "updated_by", "created_at", "updated_at")
        }),
    )
