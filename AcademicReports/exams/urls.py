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

urlpatterns = [

    
]+ router.urls