from rest_framework.permissions import BasePermission

# ==================== AcademicYear Permissions =====================
class CanViewAcademicYear(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.view_academicyear')

class CanAddAcademicYear(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.add_academicyear')

class CanChangeAcademicYear(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.change_academicyear')

# ==================== AcademicDevision Permissions =====================
class CanViewAcademicDevision(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.view_academicdevision')

class CanAddAcademicDevision(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.add_academicdevision')

class CanChangeAcademicDevision(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.change_academicdevision')

# ==================== State Permissions =====================
class CanViewState(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.view_state')

class CanAddState(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.add_state')

class CanChangeState(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.change_state')

# ==================== Zone Permissions =====================
class CanViewZone(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.view_zone')

class CanAddZone(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.add_zone')

class CanChangeZone(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.change_zone')

# ==================== Branch Permissions =====================
class CanViewBranch(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.view_branch')

class CanAddBranch(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.add_branch')

class CanChangeBranch(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('branches.change_branch')
