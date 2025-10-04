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

class CanDeleteClassName(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.delete_classname')


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

class CanDeleteOrientation(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.delete_orientation')


# ==================== Gender Permissions =====================
class CanViewGender(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.view_gender')

class CanAddGender(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.add_gender')

class CanChangeGender(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.change_gender')

class CanDeleteGender(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.delete_gender')


# ==================== AdmissionStatus Permissions =====================
class CanViewAdmissionStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.view_admissionstatus')

class CanAddAdmissionStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.add_admissionstatus')

class CanChangeAdmissionStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.change_admissionstatus')

class CanDeleteAdmissionStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.delete_admissionstatus')


# ==================== Student Permissions =====================
class CanViewStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.view_student')

class CanAddStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.add_student')

class CanChangeStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.change_student')

class CanDeleteStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('students.delete_student')


