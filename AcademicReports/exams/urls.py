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
router.register(r'co_scholastic_grade_dropdown', CoScholasticGradeDropdownViewSet, basename='co_scholastic_grade_dropdown')

router.register(r'subject', SubjectViewSet, basename='subject')
router.register(r'subjectskill', SubjectSkillViewSet, basename='subjectskill')
router.register(r'exam_type', ExamTypeViewSet, basename='exam_type')

router.register(r'exam', ExamViewSet, basename='exam')
# router.register(r'exam_instance', ExamInstanceViewSet, basename='exam_instance')
# router.register(r'exam_subject_skill_instance', ExamSubjectSkillInstanceViewSet, basename='exam_subject_skill_instance')
router.register(r'branch_wise_exam_result_status', BranchWiseExamResultStatusViewSet, basename='branch_wise_exam_result_status')

# router.register(r'subject_dropdown_for_exam_instance', SubjectDropdownForExamInstanceViewSet, basename='subject_dropdown_for_exam_instance')
router.register(r'subjectskill_dropdown_for_exam_instance', SubjectSkillDropdownForExamInstanceViewSet, basename='subjectskill_dropdown_for_exam_instance')


urlpatterns = [


        path('subject_dropdown_for_exam_instance/<int:exam_id>/', SubjectDropdownForExamInstanceViewSet.as_view({'get':'list'}), name='subject_dropdown_for_exam_instance'),
         # Make exam visible (and create branch statuses if missing)
        path('exam/<int:pk>/make-visible/',ExamMakeVisibleAPIView.as_view(),name='exam-make-visible'),
        # Make exam invisible (and hide all related branch statuses)
        path('exam/<int:pk>/make-invisible/',ExamMakeInvisibleAPIView.as_view(),name='exam-make-invisible'),
        # publish the Exam
        path("publish_the_exam/", PublishExamAPIView.as_view(), name="publish-exam"),
        path("lock_exam_marks_entry/", ExpireExamAPIView.as_view(), name="lock_exam_marks_entry"),

        path('section_wise_exam_result_status/<int:branch_id>/<int:exam_id>/', SectionWiseExamResultStatusViewSet.as_view({'get': 'list'}),name='section_wise_exam_result_status'),
        path('update_section_wise_exam_result_status_view/', update_section_wise_exam_result_status_view, name='update_section_wise_exam_result_status_view'),

        path('exam_instance/<int:exam_id>/', ExamInstanceViewSet.as_view({'get': 'list','post': 'create'}), name='examinstance-list'),
        path('exam_instance/<int:exam_id>/<int:pk>/', ExamInstanceViewSet.as_view({'get': 'retrieve','put': 'update'}), name='examinstance-retrive'),
        path('exam_subject_skill_instance/<int:exam_instance_id>/',ExamSubjectSkillInstanceViewSet.as_view({'get': 'list'}),name='exam_subject_skill_instance_list'),
        path('exam_subject_skill_instance/<int:exam_instance_id>/<int:pk>/',ExamSubjectSkillInstanceViewSet.as_view({'get': 'retrieve', 'put': 'update'}),name='exam_subject_skill_instance_retrieve'),

        path('create_exam_results/', create_exam_results, name='create_exam_results'),
        path('edit_exam_results/<int:exam_result_id>/', edit_exam_results, name='edit_exam_results'),
        path('edit_exam_skill_result/<int:exam_skill_result_id>/', edit_exam_skill_result, name='edit_exam_skill_result'),



    
]+ router.urls