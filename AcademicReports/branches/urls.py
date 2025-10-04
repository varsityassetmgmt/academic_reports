from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'academic_devision_dropdown', AcademicDevisionDropdownViewSet, basename='academic_devision_dropdown')
router.register(r'state_dropdown', StateDropdownViewSet, basename='state_dropdown')
router.register(r'zone_dropdown', ZoneDropdownViewSet, basename='zone_dropdown')
router.register(r'branch_dropdown', BranchDropdownViewSet, basename='branch_dropdown')

router.register(r'state_dropdown_for_exam', StateDropdownForExamViewSet, basename='state_dropdown_for_exam')
router.register(r'zone_dropdown_for_exam', ZoneDropdownForExamViewSet, basename='zone_dropdown_for_exam')
router.register(r'branch_dropdown_for_exam', BranchDropdownForExamViewSet, basename='branch_dropdown_for_exam')



urlpatterns = [

    
]+ router.urls

