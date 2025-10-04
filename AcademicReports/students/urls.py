from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'classname_dropdown', ClassNameDropdownViewSet, basename='classname_dropdown')
router.register(r'orientation_dropdown', OrientationDropdownViewSet, basename='orientation_dropdown')

router.register(r'classname_dropdown_for_exam', ClassNameDropdownForExamViewSet, basename='classname_dropdown_for_exam')
router.register(r'orientation_dropdown_for_exam', OrientationDropdownForExamViewSet, basename='orientation_dropdown_for_exam')

urlpatterns = [

    
]+ router.urls