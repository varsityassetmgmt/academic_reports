from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from exams.models import StudentExamSummary
from apisource.serializers import *
from usermgmt.custompagination import CustomPagination
from students.models import *
from rest_framework.permissions import IsAuthenticated
 
from usermgmt.authentication import QueryParameterTokenAuthentication
from rest_framework.authentication import ( SessionAuthentication, TokenAuthentication )
 

class StudentProgressCardsListForWebsiteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentProgressCardsListForWebsiteSerializer
    pagination_class = CustomPagination
    http_method_names = ['get']
    authentication_classes = [QueryParameterTokenAuthentication,SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        scs_number = self.request.query_params.get('scs_number')
        academic_year_id = self.request.query_params.get('academic_year_id')

        if not scs_number or not academic_year_id:
            return StudentExamSummary.objects.none()
        queryset = (
            StudentExamSummary.objects.filter(
                student__SCS_Number__iexact=scs_number,
                academic_year_id=academic_year_id,
                is_active=True,
                is_progresscard=True
            )
            .select_related('student', 'exam', 'academic_year')
            .order_by('students_exam_summary_id')  # fixes pagination warning
        )
        return queryset

    def list(self, request, *args, **kwargs):
        scs_number = request.query_params.get('scs_number')
        academic_year_id = request.query_params.get('academic_year_id')

        if not scs_number or not academic_year_id:
            return Response(
                {"detail": "Both 'scs_number' and 'academic_year_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"detail": "No progress card records found for the given details."},
                status=status.HTTP_404_NOT_FOUND
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

     
