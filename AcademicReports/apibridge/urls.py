from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path 
from apibridge.views import *
from rest_framework.routers import DefaultRouter




urlpatterns = [  
    path('get_states_varna/',get_states_varna), 
    path('get_zones_varna/',get_zones_varna),
    path("get_branches_varna/",get_branches_varna),
    path('get_academic_years/',get_academic_years),
    path('get_orientations_varna_api/',get_orientations_varna_api),
    path('get_class_names_school_api/',get_class_names_school_api),

    

    # # path("get_po_header_varna/",get_po_header_varna),

    # path('test/',test,name='test'),

    path('trigger_process_all_branches_sections/',trigger_process_all_branches_sections),
    path('trigger_process_all_branches_students/',trigger_process_all_branches_students),


    #=============================================================   Employees  ===================================================================================================================
    # path('get_departments_from_varna/',get_departments_from_varna),
    # path('get_designation_from_varna/',get_designation_from_varna),

    # path('get_scts_teachers_from_varna/<int:branch_id>/',get_scts_teachers_from_varna),
    # path('sync_all_scts_branches_teachers/', trigger_all_scts_branches_teacher_sync, name='sync_all_teachers'),
    
    

    
    #===================================  New URls Start  ===========================================================================================================

    # path('get_states_from_scts_school_api/',get_states_from_scts_school_api),
    # path('get_zones_from_scts_school_api/',get_zones_from_scts_school_api),
    # path('get_branches_from_scts_school_api/',get_branches_from_scts_school_api),
    # path('get_departments_from_scts_school_api/',get_departments_from_scts_school_api),
    # path('get_designation_from_scts_school_api/',get_designation_from_scts_school_api),
    # # path('get_scts_teachers_from_varna/<int:branch_id>/',get_scts_teachers_from_varna),
    # path('sync_all_scts_branches_teachers/', trigger_all_scts_branches_teacher_sync, name='sync_scts_all_teachers'),
    # path('update_scts_branch_score_centers/',update_scts_branch_score_centers),


    # path('get_states_from_telangana_school_api/',get_states_from_telangana_school_api),
    # path('get_zones_from_telangana_school_api/',get_zones_from_telangana_school_api),
    # path('get_branches_from_telangana_school_api/',get_branches_from_telangana_school_api),
    # path('get_departments_from_telangana_school_api/',get_departments_from_telangana_school_api),
    # path('get_designation_from_telangana_school_api/',get_designation_from_telangana_school_api),
    # path('sync_all_telangana_branches_teachers/', trigger_all_telangana_branches_teacher_sync, name='sync_telangana_all_teachers'),
    # path('update_telangana_branch_score_centers/',update_telangana_branch_score_centers),

    #===================================  New URLS END     ===========================================================================================================




    # Testing 
    # path('testing_process_sections/<int:branch_id>/', views.process_sections_api, name='process_sections_api'),

    path('sync_all_varna_user/',SyncAllVarnaUsersAPIView.as_view()),
    path("sync_user_profiles_from_varna/",SyncVarnaUserProfileBranchesAPIView.as_view()),
 
]

router = DefaultRouter()
# router.register(r'users',UserViewset,basename='api_users')

urlpatterns += router.urls