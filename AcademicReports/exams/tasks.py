from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from exams.models import (
    SectionWiseExamResultStatus,
    ExamInstance,
    ExamSubjectSkillInstance,
    ExamResult,
    ExamSkillResult,
)
from students.models import Student
from .models import GradeBoundary, StudentExamSummary
import logging

logger = logging.getLogger(__name__)

@shared_task
def create_update_student_exam_summary(section_wise_exam_result_status_id):
    """
    Background task to create or update student exam summaries.
    """
    if not section_wise_exam_result_status_id:
        logger.error("Missing section_wise_exam_result_status_id")
        return {"status": "error", "message": "section_wise_exam_result_status_id is required"}

    try:
        section_status = SectionWiseExamResultStatus.objects.get(
            id=section_wise_exam_result_status_id, is_active=True
        )
    except ObjectDoesNotExist:
        logger.error(f"Invalid SectionWiseExamResultStatus ID: {section_wise_exam_result_status_id}")
        return {"status": "error", "message": "Invalid section_wise_exam_result_status_id"}

    # if section_status.marks_completion_percentage != 100:
    #     logger.info(
    #         f"Marks not completed for section {section_status.id}: "
    #         f"{section_status.marks_completion_percentage}% done"
    #     )
    #     return {
    #         "status": "incomplete",
    #         "message": f"Marks entry not completed ({section_status.marks_completion_percentage}%)"
    #     }

    exam = section_status.exam
    exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True).exclude(is_optional=True)
    skill_instances = ExamSubjectSkillInstance.objects.filter(
        exam_instance__in=exam_instances, is_active=True
    )

    students = Student.objects.filter(
        section=section_status.section,
        is_active=True,
        academic_year=exam.academic_year,
    ).exclude(admission_status__admission_status_id=3)

    exam_results = ExamResult.objects.filter(
        student__in=students,
        exam_instance__in=exam_instances,
        is_active=True
    ).select_related("student", "exam_instance", "exam_attendance", "co_scholastic_grade")


    skill_results = ExamSkillResult.objects.filter(exam_result__exam_result_id__in= exam_results.values_list('exam_result_id', flat=True))

    # Pre-compute total maximum marks (same for all students)
    total_subjects_maximum = exam_instances.aggregate(
        total_ext=Sum("maximum_marks_external"),
        total_int=Sum("maximum_marks_internal")
    )
    total_subjects_maximum_marks = (total_subjects_maximum["total_ext"] or 0) + (total_subjects_maximum["total_int"] or 0)

    total_skills_maximum = skill_instances.aggregate(
        total_ext=Sum("maximum_marks_external"),
        total_int=Sum("maximum_marks_internal")
    )
    total_skills_maximum_marks = (total_skills_maximum["total_ext"] or 0) + (total_skills_maximum["total_int"] or 0)

    # Create/update summaries for each student
    for student in students:
        student_results = exam_results.filter(student=student)
        total_subjects_obtained = student_results.aggregate(
            total_marks_obt=Sum("total_marks")
        )
        total_subjects_obtained_marks = total_subjects_obtained["total_marks_obt"] or 0

        # Calculate percentage safely
        subjects_percentage = (
            (total_subjects_obtained_marks / total_subjects_maximum_marks) * 100
            if total_subjects_maximum_marks > 0
            else 0
        )

        # Determine grade
        subject_grade = GradeBoundary.objects.filter(
            category = exam.category,
            min_percentage__lte=subjects_percentage,
            max_percentage__gte=subjects_percentage,
            is_active=True
        ).first()

        student_skill_results = skill_results.filter(exam_result__exam_result_id__in = student_results.values_list('exam_result_id', flat=True))
        total_skills_obtained = student_skill_results.aggregate(
            total_skill_marks_obt = Sum('marks_obtained')
        )
        total_skills_obtained_marks = total_skills_obtained['total_skill_marks_obt'] or 0
        skills_percentage = (
            (total_skills_obtained_marks/total_skills_maximum_marks)*100
            if total_skills_maximum_marks >0
            else 0
        )

        skills_grade = GradeBoundary.objects.filter(
            category = exam.category,
            min_percentage__lte=skills_percentage,
            max_percentage__gte=skills_percentage,
            is_active=True
        ).first()

        student_exam_summary, created = StudentExamSummary.objects.update_or_create(
            student=student,
            exam=exam,
            # academic_year = exam.academic_year,
            defaults={
                "total_subjects_maximum_marks": total_subjects_maximum_marks,
                "total_skills_maximum_marks": total_skills_maximum_marks,
                "total_subjects_obtained_marks": total_subjects_obtained_marks,
                "subjects_percentage": subjects_percentage,
                "subject_grade": subject_grade,
                "total_skills_obtained_marks":total_skills_obtained_marks,
                "skills_percentage":skills_percentage,
                "skills_grade":skills_grade,
                "academic_year":exam.academic_year,
            },
        )

        # logger.info(
        #     f"{'Created' if created else 'Updated'} exam summary for student {student.id} "
        #     f"({student.name}) in section {section_status.section.name} - "
        #     f"{subjects_percentage:.2f}% ({subject_grade})"
        # )

    return {"status": "success", "message": "Student exam summaries updated successfully"}


# from celery import shared_task
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Sum
# from exams.models import (
#     SectionWiseExamResultStatus,
#     ExamInstance,
#     ExamSubjectSkillInstance,
#     ExamResult,
#     ExamSkillResult,
# )
# from students.models import Student
# from .models import GradeBoundary, StudentExamSummary
# import logging

# logger = logging.getLogger(__name__)

# @shared_task
# def create_update_student_exam_summary(section_wise_exam_result_status_id):
#     """
#     Background task to create or update student exam summaries.
#     """
#     if not section_wise_exam_result_status_id:
#         logger.error("Missing section_wise_exam_result_status_id")
#         return {"status": "error", "message": "section_wise_exam_result_status_id is required"}

#     try:
#         section_status = SectionWiseExamResultStatus.objects.get(
#             id=section_wise_exam_result_status_id, is_active=True
#         )
#     except ObjectDoesNotExist:
#         logger.error(f"Invalid SectionWiseExamResultStatus ID: {section_wise_exam_result_status_id}")
#         return {"status": "error", "message": "Invalid section_wise_exam_result_status_id"}

#     exam = section_status.exam
#     exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True)
#     skill_instances = ExamSubjectSkillInstance.objects.filter(
#         exam_instance__in=exam_instances, is_active=True
#     )

#     students = Student.objects.filter(
#         section=section_status.section,
#         is_active=True,
#         academic_year=exam.academic_year,
#     ).exclude(admission_status__admission_status_id=3)

#     exam_results = ExamResult.objects.filter(
#         student__in=students,
#         exam_instance__in=exam_instances,
#         is_active=True
#     ).select_related("student", "exam_instance")

#     exam_result_ids = list(exam_results.values_list('exam_result_id', flat=True))
#     skill_results = ExamSkillResult.objects.filter(exam_result_id__in=exam_result_ids)

#     # Precompute lookups
#     results_by_student = {}
#     for res in exam_results:
#         results_by_student.setdefault(res.student_id, []).append(res)

#     skill_results_by_student = {}
#     for skill in skill_results:
#         sid = skill.exam_result.student_id
#         skill_results_by_student.setdefault(sid, []).append(skill)

#     # Pre-compute total maximum marks (same for all students)
#     total_subjects_maximum = exam_instances.aggregate(
#         total_ext=Sum("maximum_marks_external"),
#         total_int=Sum("maximum_marks_internal")
#     )
#     total_subjects_maximum_marks = (total_subjects_maximum["total_ext"] or 0) + (total_subjects_maximum["total_int"] or 0)

#     total_skills_maximum = skill_instances.aggregate(
#         total_ext=Sum("maximum_marks_external"),
#         total_int=Sum("maximum_marks_internal")
#     )
#     total_skills_maximum_marks = (total_skills_maximum["total_ext"] or 0) + (total_skills_maximum["total_int"] or 0)

#     # Create/update summaries for each student
#     for student in students:
#         student_results = results_by_student.get(student.id, [])
#         total_subjects_obtained_marks = sum(res.total_marks or 0 for res in student_results)

#         subjects_percentage = (
#             float(total_subjects_obtained_marks) / float(total_subjects_maximum_marks) * 100
#             if total_subjects_maximum_marks > 0 else 0
#         )

#         subject_grade = GradeBoundary.objects.filter(
#             min_percentage__lte=subjects_percentage,
#             max_percentage__gte=subjects_percentage,
#             is_active=True
#         ).first()

#         student_skill_results = skill_results_by_student.get(student.id, [])
#         total_skills_obtained_marks = sum(s.marks_obtained or 0 for s in student_skill_results)

#         skills_percentage = (
#             float(total_skills_obtained_marks) / float(total_skills_maximum_marks) * 100
#             if total_skills_maximum_marks > 0 else 0
#         )

#         skills_grade = GradeBoundary.objects.filter(
#             min_percentage__lte=skills_percentage,
#             max_percentage__gte=skills_percentage,
#             is_active=True
#         ).first()

#         student_exam_summary, created = StudentExamSummary.objects.update_or_create(
#             student=student,
#             exam=exam,
#             defaults={
#                 "total_subjects_maximum_marks": total_subjects_maximum_marks,
#                 "total_skills_maximum_marks": total_skills_maximum_marks,
#                 "total_subjects_obtained_marks": total_subjects_obtained_marks,
#                 "subjects_percentage": subjects_percentage,
#                 "subject_grade": subject_grade,
#                 "total_skills_obtained_marks": total_skills_obtained_marks,
#                 "skills_percentage": skills_percentage,
#                 "skills_grade": skills_grade,
#             },
#         )

#         grade_label = getattr(subject_grade, "grade_name", None) or getattr(subject_grade, "name", "")
#         logger.info(
#             f"{'Created' if created else 'Updated'} summary for {student.name}: "
#             f"{subjects_percentage:.2f}% ({grade_label})"
#         )

#     return {"status": "success", "message": "Student exam summaries updated successfully"}

@shared_task
def update_exam_result_grade(exam_result_id):
    try:
        instance = ExamResult.objects.get(exam_result_id = exam_result_id)
        exam = instance.exam_instance.exam
        percentage = instance.percentage

        # ✅ Guard against missing data
        if not percentage:
            return
        
        # external = self.external_marks or 0
        # internal = self.internal_marks or 0
        # self.total_marks = external + internal

        # # --- Compute percentage safely ---
        # max_external = getattr(self.exam_instance, "maximum_marks_external", 0) or 0
        # max_internal = getattr(self.exam_instance, "maximum_marks_internal", 0) or 0
        # total_max = max_external + max_internal

        # if total_max > 0:
        #     self.percentage = (self.total_marks / total_max) * 100
        # else:
        #     self.percentage = None

        if exam and exam.category:
            grade = GradeBoundary.objects.filter(
                category=exam.category,
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                is_active=True
            ).first()
        else:
            # fallback: use default boundaries (category is null)
            grade = GradeBoundary.objects.filter(
                category__isnull=True,
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                is_active=True
            ).first()

        if grade:
            ExamResult.objects.filter(pk=instance.pk).update(grade=grade)

    except ExamResult.DoesNotExist:
        pass


@shared_task
def update_exam_skill_result_grade(exam_skill_result_id):
    try:
        instance = ExamSkillResult.objects.get(pk=exam_skill_result_id)
        exam = instance.exam_result.exam_instance.exam
        percentage = instance.percentage

        # ✅ Guard against missing percentage
        if not percentage:
            return

        if exam and exam.category:
            grade = GradeBoundary.objects.filter(
                category=exam.category,
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                is_active=True
            ).first()
        else:
            # fallback: use default boundaries (category is null)
            grade = GradeBoundary.objects.filter(
                category__isnull=True,
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                is_active=True
            ).first()

        if grade:
            ExamSkillResult.objects.filter(pk=instance.pk).update(grade=grade)

    except ExamSkillResult.DoesNotExist:
        pass
