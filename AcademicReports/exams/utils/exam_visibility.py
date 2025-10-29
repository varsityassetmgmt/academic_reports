
# utils/exam_visibility.py
from django.utils import timezone
from django.db import transaction
from exams.models import *

def set_exam_visibility(exam, user=None, visible=True):
     
    now = timezone.now()

    # If trying to make visible but expiry passed
    if visible and exam.marks_entry_expiry_datetime and exam.marks_entry_expiry_datetime < now:
        return {
            "success": False,
            "message": f"Cannot make '{exam.name}' visible — marks entry time has expired.",
            "exam_id": exam.exam_id,
            "is_visible": exam.is_visible,
        }

    with transaction.atomic():
        # Update exam visibility
        exam.is_visible = visible
        if user:
            exam.updated_by = user
        exam.save(update_fields=["is_visible", "updated_by"] if user else ["is_visible"])

        if visible:
            # Fetch branches
            branches = list(exam.branches.all())
            branch_ids = [b.branch_id for b in branches]

            # Existing branch statuses
            existing = set(BranchWiseExamResultStatus.objects.filter(academic_year =  exam.academic_year,exam=exam,branch_id__in=branch_ids).values_list("branch_id", flat=True))
            default_status = ExamResultStatus.objects.filter(name__iexact="Not Started").first()

            new_objects = [
                            BranchWiseExamResultStatus(
                                exam=exam,
                                branch_id=bid,
                                academic_year=exam.academic_year,
                                status=default_status,
                                is_visible=True,
                                is_active=True,
                                marks_entry_expiry_datetime=exam.marks_entry_expiry_datetime,
                            )
                            for bid in branch_ids if bid not in existing
                        ]
            BranchWiseExamResultStatus.objects.bulk_create(new_objects, ignore_conflicts=True)
            branch_updated_count = len(new_objects)
        else:
           
            branch_updated_count = BranchWiseExamResultStatus.objects.filter(exam=exam, is_visible=True).update(is_visible=False)

    return {
        "success": True,
        "message": f"Exam '{exam.name}' visibility updated.",
        "exam_id": exam.exam_id,
        "is_visible": visible,
        "branches_updated": branch_updated_count,
    }
