from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from usermgmt.models import *

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'name', 'codename')
    search_fields = ('id', 'name', 'content_type__model', 'codename')


# ================== Inline Profile inside User ==================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    full_name.short_description = "Full Name"

    list_display = ("username", "full_name", "email", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "first_name", "last_name", "email")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # Ensure both first_name and last_name are included in search
        extra_qs = self.model.objects.filter(first_name__icontains=search_term) | \
                   self.model.objects.filter(last_name__icontains=search_term)
        return queryset | extra_qs, use_distinct

    def get_inline_instances(self, request, obj=None):
        """Show inline only when editing an existing User"""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# ================== Standalone UserProfile Admin ==================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "varna_user_id",
        "varna_profile",
        "varna_user",
        "must_change_password",
        "is_varna_user_first_login",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "phone_number",
        "varna_user_id",
        "varna_profile_short_code",
    )
    list_filter = (
        "varna_user",
        "must_change_password",
        "is_varna_user_first_login",
        "branches",
        "varna_profile",
    )
    filter_horizontal = (
        "states",
        "zones",
        "branches",
        "academic_devisions",
        "classes",
        "orientations",
    )
    readonly_fields = ("varna_user_id",)
    ordering = ("user__username",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "photo", "bio", "phone_number"),
        }),
        ("Varna Integration", {
            "fields": (
                "varna_user",
                "varna_user_id",
                "varna_profile_short_code",
                "varna_profile",
                "is_varna_user_first_login",
            ),
        }),
        ("Access & Relations", {
            "fields": (
                "states",
                "zones",
                "branches",
                "academic_devisions",
                "classes",
                "orientations",
            ),
        }),
        ("Security", {
            "fields": ("must_change_password",),
        }),
    )


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(VarnaProfiles)
class VarnaProfilesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "varna_profile_short_code",
        'varna_profile_id',
        "is_active",
    )
    list_filter = ("is_active", "groups")
    search_fields = ("name",'varna_profile_id', "varna_profile_short_code")
    filter_horizontal = ("groups",)
    ordering = ("name",)

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "varna_profile_short_code",
                'varna_profile_id',
                "groups",
                "is_active",
            ),
        }),
    )