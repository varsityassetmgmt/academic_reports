from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'classname_dropdown', ClassNameDropdownViewSet, basename='classname_dropdown')
router.register(r'orientation_dropdown', OrientationDropdownViewSet, basename='orientation_dropdown')

urlpatterns = [

    
]+ router.urls