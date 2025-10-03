from rest_framework.permissions import BasePermission

# ==================== Subject Permissions =====================
class CanViewSubject(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_subject')

class CanAddSubject(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_subject')

class CanChangeSubject(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_subject')

class CanDeleteSubject(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_subject')


# ==================== SubjectSkill Permissions =====================
class CanViewSubjectSkill(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_subjectskill')

class CanAddSubjectSkill(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_subjectskill')

class CanChangeSubjectSkill(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_subjectskill')

class CanDeleteSubjectSkill(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_subjectskill')


# ==================== ExamType Permissions =====================
class CanViewExamType(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_examtype')

class CanAddExamType(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_examtype')

class CanChangeExamType(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_examtype')

class CanDeleteExamType(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_examtype')


# ==================== Exam Permissions =====================
class CanViewExam(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_exam')

class CanAddExam(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_exam')

class CanChangeExam(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_exam')

class CanDeleteExam(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_exam')


# ==================== ExamInstance Permissions =====================
class CanViewExamInstance(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_examinstance')

class CanAddExamInstance(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_examinstance')

class CanChangeExamInstance(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_examinstance')

class CanDeleteExamInstance(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_examinstance')


# ==================== ExamAttendanceStatus Permissions =====================
class CanViewExamAttendanceStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_examattenancestatus')

class CanAddExamAttendanceStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_examattenancestatus')

class CanChangeExamAttendanceStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_examattenancestatus')

class CanDeleteExamAttendanceStatus(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_examattenancestatus')


# ==================== GradeBoundary Permissions =====================
class CanViewGradeBoundary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_gradeboundary')

class CanAddGradeBoundary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_gradeboundary')

class CanChangeGradeBoundary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_gradeboundary')

class CanDeleteGradeBoundary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_gradeboundary')


# ==================== ExamResult Permissions =====================
class CanViewExamResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_examresult')

class CanAddExamResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_examresult')

class CanChangeExamResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_examresult')

class CanDeleteExamResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_examresult')


# ==================== ExamSkillResult Permissions =====================
class CanViewExamSkillResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_examskillresult')

class CanAddExamSkillResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_examskillresult')

class CanChangeExamSkillResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_examskillresult')

class CanDeleteExamSkillResult(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_examskillresult')


# ==================== StudentExamSummary Permissions =====================
class CanViewStudentExamSummary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.view_studentexamsummary')

class CanAddStudentExamSummary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.add_studentexamsummary')

class CanChangeStudentExamSummary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.change_studentexamsummary')

class CanDeleteStudentExamSummary(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('exams.delete_studentexamsummary')
