from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'subject_dropdown', SubjectDropdownViewSet, basename='subject_dropdown')
router.register(r'subjectskill_dropdown', SubjectSkillDropdownViewSet, basename='subjectskill_dropdown')
router.register(r'examtype_dropdown', ExamTypeDropdownViewSet, basename='examtype_dropdown')
router.register(r'exam_dropdown', ExamDropdownViewSet, basename='exam_dropdown')
router.register(r'examinstance_dropdown', ExamInstanceDropdownViewSet, basename='examinstance_dropdown')
router.register(r'examattendancestatus_dropdown', ExamAttendanceStatusDropdownViewSet, basename='examattendancestatus_dropdown')

router.register(r'subject', SubjectViewSet, basename='subject')
router.register(r'subjectskill', SubjectSkillViewSet, basename='subjectskill')
router.register(r'exam_type', ExamTypeViewSet, basename='exam_type')

router.register(r'exam', ExamViewSet, basename='exam')
router.register(r'exam_instance', ExamInstanceViewSet, basename='exam_instance')
router.register(r'exam_subject_skill_instance', ExamSubjectSkillInstanceViewSet, basename='exam_subject_skill_instance')
router.register(r'branch_wise_exam_result_status', BranchWiseExamResultStatusViewSet, basename='branch_wise_exam_result_status')

router.register(r'subject_dropdown_for_exam_instance', SubjectDropdownForExamInstanceViewSet, basename='subject_dropdown_for_exam_instance')
router.register(r'subjectskill_dropdown_for_exam_instance', SubjectSkillDropdownForExamInstanceViewSet, basename='subjectskill_dropdown_for_exam_instance')


urlpatterns = [

    
]+ router.urls