from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'classname_dropdown', ClassNameDropdownViewSet, basename='classname_dropdown')
router.register(r'orientation_dropdown', OrientationDropdownViewSet, basename='orientation_dropdown')

router.register(r'classname_dropdown_for_students', ClassNameDropdownForStudentsViewSet, basename='classname_dropdown_for_students')
router.register(r'orientation_dropdown_for_students', OrientationDropdownForStudentsViewSet, basename='orientation_dropdown_for_students')
router.register(r'admission_status_dropdown_for_students', AdmissionStatusDropdownForStudentsViewSet, basename='admission_status_dropdown_for_students')

router.register(r'classname_dropdown_for_exam', ClassNameDropdownForExamViewSet, basename='classname_dropdown_for_exam')
router.register(r'orientation_dropdown_for_exam', OrientationDropdownForExamViewSet, basename='orientation_dropdown_for_exam')

router.register(r'students', StudentViewSet, basename='students')
router.register(r'sections', SectionViewSet, basename='sections')

urlpatterns = [

    path('get_branch_wise_orientations/',trigger_branch_orientation_sync),
]+ router.urls