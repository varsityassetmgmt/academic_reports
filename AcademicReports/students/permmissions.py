from rest_framework.permissions import BasePermission

# ==================== ClassName Permissions =====================
class CanViewClassName(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.view_classname')

class CanAddClassName(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.add_classname')

class CanChangeClassName(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.change_classname')

# ==================== Orientation Permissions =====================
class CanViewOrientation(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.view_orientation')

class CanAddOrientation(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.add_orientation')

class CanChangeOrientation(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.change_orientation')
