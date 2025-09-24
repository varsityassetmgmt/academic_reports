from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission

from .models import UserProfile

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'name', 'codename')
    search_fields = ('id', 'name', 'content_type__model', 'codename')

# Inline admin for UserProfile (shows profile fields inside User admin page)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


# Custom User admin with UserProfile inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # Full name display
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    full_name.short_description = "Full Name"

    list_display = ("username", "full_name", "email", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")

    # Add search fields (fullname supported via icontains query on first_name/last_name)
    search_fields = ("username", "first_name", "last_name", "email")

    def get_search_results(self, request, queryset, search_term):
        # Extend default search to include "full_name"
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return (
            queryset | self.model.objects.filter(first_name__icontains=search_term)
                                         .filter(last_name__icontains=search_term),
            use_distinct,
        )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Separate admin for UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    full_name.short_description = "Full Name"

    list_display = ("user", "full_name", "phone_number", "must_change_password")
    list_filter = ("must_change_password", "states", "zones", "branches", "academic_devisions")

    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return (
            queryset | self.model.objects.filter(user__first_name__icontains=search_term)
                                         .filter(user__last_name__icontains=search_term),
            use_distinct,
        )

    filter_horizontal = ("states", "zones", "branches", "academic_devisions")


# Replace the default User admin with the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
