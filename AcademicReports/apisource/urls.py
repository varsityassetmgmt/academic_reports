from django.urls import path
from apisource.views import *
from progresscard.views import DownloadProgressCardWebsiteAPIView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

# router.register(r'subject_dropdown', SubjectDropdownViewSet, basename='subject_dropdown')
 

urlpatterns = [
    
    path("student_progress_cards_list_for_website/", StudentProgressCardsListForWebsiteViewSet.as_view({'get': 'list'})),

    path("download_progress_card_website/",DownloadProgressCardWebsiteAPIView.as_view())
    

    
    



]+ router.urls