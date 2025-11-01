from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from exams.models import BranchWiseExamResultStatus
from usermgmt.models import UserProfile
from branches.models import Branch, AcademicYear
from students.models import Student
from rest_framework.exceptions import NotFound
from rest_framework import permissions, status

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    current_academic_year = AcademicYear.objects.filter(is_current_academic_year=True).first()
    if not current_academic_year:
        raise NotFound("Current academic year not found.")

    user = request.user

    # --- Determine accessible branches ---
    if user.is_superuser:
        branches_qs = Branch.objects.filter(is_active=True)
    else:
        user_branch_ids = (
            UserProfile.objects.filter(user=user)
            .values_list('branches__branch_id', flat=True)
            .distinct()
        )
        branches_qs = Branch.objects.filter(is_active=True, branch_id__in=user_branch_ids)

    # --- Student count ---
    total_students_count = Student.objects.filter(
        academic_year=current_academic_year,
        branch__branch_id__in=branches_qs.values_list('branch_id', flat=True),
        student_class__is_active=True,
        is_active=True,
    ).exclude(admission_status=3).count()  # Excluding Dropout Students

    # --- Exam result status ---
    total_exams_conducted = BranchWiseExamResultStatus.objects.filter(
        academic_year=current_academic_year,
        branch__in=branches_qs,
        is_active=True,
    )

    total_exams_conducted_count = total_exams_conducted.count()
    from collections import Counter
    status_counts = Counter(total_exams_conducted.values_list('status_id', flat=True))

    response_data = {
        "total_students_count": total_students_count,
        "total_exams_conducted_count": total_exams_conducted_count,
        "marks_entry_not_yet_started_exams_count": status_counts.get(1, 0),
        "marks_entry_inprogress_exams_count": status_counts.get(2, 0),
        "marks_entry_completed_exams_count": status_counts.get(3, 0),
        "marks_entry_finalized_exams_count": status_counts.get(4, 0),
    }

    return Response(response_data, status=status.HTTP_200_OK)
