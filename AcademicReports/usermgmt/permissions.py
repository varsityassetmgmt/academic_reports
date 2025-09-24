from rest_framework.permissions import BasePermission


# ================= User Permissions =====================
class CanViewUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.view_user')

class CanAddUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.add_user')

class CanChangeUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.change_user')

# Password Change Permission
class CanChangePassword(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.change_password_by_admin')


# ================= UserProfile Permissions =====================
class CanViewUserProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('usermgmt.view_userprofile')

class CanAddUserProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('usermgmt.add_userprofile')

class CanChangeUserProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('usermgmt.change_userprofile')

from rest_framework.permissions import BasePermission


# ================= Group Permissions =====================
class CanViewGroup(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.view_group')

class CanAddGroup(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.add_group')

class CanChangeGroup(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('auth.change_group')


