from django.urls import path
from progresscard.views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

# router.register(r'subject_dropdown', SubjectDropdownViewSet, basename='subject_dropdown')
 

urlpatterns = [
    
    path("download_progress_card/", DownloadProgressCardAPIView.as_view(), name="download_progress_card"),
    path('bulk_download_progress_cards/',DownloadBulkProgressCardsAPIView.as_view()),
    path('bulk_download_progress_cards_zip_file/',BulkProgressCardDownloadZipFileAPIView.as_view()),



]+ router.urls