from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import UserProfile


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
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    full_name.short_description = "Full Name"

    def image_preview(self, obj):
        if obj.photo and obj.photo.url:
            return format_html('<img src="{}" style="width:50px; height:50px; border-radius:50%;" />', obj.photo.url)
        return "No Image"
    image_preview.short_description = "Profile Photo"

    list_display = ("user", "full_name", "phone_number", "must_change_password", "image_preview")
    list_filter = ("must_change_password", "states", "zones", "branches", "academic_devisions", "classes", "orientations")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email", "phone_number")
    filter_horizontal = ("states", "zones", "branches", "academic_devisions", "classes", "orientations")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        extra_qs = self.model.objects.filter(user__first_name__icontains=search_term) | \
                   self.model.objects.filter(user__last_name__icontains=search_term)
        return queryset | extra_qs, use_distinct


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

