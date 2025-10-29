from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'users', UserViewset, basename='users')
router.register(r'user_profiles', UserProfileViewSet, basename='user_profiles')
router.register(r'groups', GroupViewSet, basename='groups')


router.register(r'academic_divisions_dropdown_for_user_profile', AcademicDevisionDropdownForUserProfileViewSet, basename='academic_divisions_dropdown_for_user_profile')
router.register(r'state_dropdown_for_user_profile', StateDropdownForUserProfileViewSet, basename='state_dropdown_for_user_profile')
router.register(r'zones_dropdown_for_user_profile', ZoneDropdownForUserProfileViewSet, basename='zones_dropdown_for_user_profile')
router.register(r'branches_dropdown_for_user_profile', BranchDropdownForUserProfileViewSet, basename='branches_dropdown_for_user_profile')
router.register(r'class_names_dropdown_for_user_proflie', ClassNameDropdownForUserProfileViewSet, basename='class_names_dropdown_for_user_proflie')
router.register(r'orientation_dropdown_for_user_profile', OrientationDropdownForUserProfileViewSet, basename='orientation_dropdown_for_user_profile')

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name="login"),
    path('change_password_first_login/',change_password_first_login),
    path('change_password_by_user/',change_password_by_user),   #for User
    path('changepassword_by_admin/<int:user_id>/',user_change_password_by_admin), # for Admin

    path('groups_dropdown/', get_groups_dropdown, name='groups_dropdown'),
    path('permissions_dropdown/', get_permissions_dropdown, name='permissions_dropdown'),   # for Groups
    path('permissions_dropdown_exclude_groups/<str:group_list>/', get_permissions_dropdown_exclude_groups, name='permissions_dropdown_exclude_groups'),  # for Users
    path('varna_user_data/',VarnaUserDataAPIView.as_view()),
]+ router.urls