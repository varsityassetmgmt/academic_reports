from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from exams.models import *
from students.models import Student
from .models import GradeBoundary, StudentExamSummary
import logging
from django.db.models import Q
from decimal import Decimal

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
        exam_result = ExamResult.objects.get(exam_result_id=exam_result_id)
    except ExamResult.DoesNotExist:
        return

    exam_instance = exam_result.exam_instance
    exam = getattr(exam_instance, "exam", None)
    total_marks = (exam_result.external_marks or 0) + (exam_result.internal_marks or 0)

    max_external = getattr(exam_instance, "maximum_marks_external", 0) or 0
    max_internal = getattr(exam_instance, "maximum_marks_internal", 0) or 0
    total_max = max_external + max_internal

    percentage = exam_result.percentage or ((total_marks / total_max) * 100 if total_max > 0 else None)

    # if not percentage:
    #     return

    grade_qs = GradeBoundary.objects.filter(
        min_percentage__lte=percentage,
        max_percentage__gte=percentage,
        is_active=True
    )

    if exam and exam.category:
        grade_qs = grade_qs.filter(category=exam.category)
    else:
        grade_qs = grade_qs.filter(category__isnull=True)

    grade = grade_qs.first()

    if grade:
        ExamResult.objects.filter(exam_result_id=exam_result_id).update(
            total_marks=total_marks,
            percentage=percentage,
            grade=grade
        )


@shared_task
def update_exam_skill_result_grade(exam_skill_result_id):
    try:
        exam_skill_result = ExamSkillResult.objects.get(exam_skill_result_id=exam_skill_result_id)
        exam = exam_skill_result.exam_result.exam_instance.exam

        external = exam_skill_result.external_marks or 0
        internal = exam_skill_result.internal_marks or 0
        marks_obtained = external + internal

        exam_instance = exam_skill_result.exam_result.exam_instance

        exam_skill_instance = (
            ExamSubjectSkillInstance.objects.filter(
                exam_instance=exam_instance,
                subject_skill=exam_skill_result.skill,
                is_active=True
            )
            .only("maximum_marks_external", "maximum_marks_internal", "has_external_marks", "has_internal_marks")
            .first()
        )

        max_external = 0
        max_internal = 0
        if exam_skill_instance:
            if getattr(exam_skill_instance, "has_external_marks", False):
                max_external = getattr(exam_skill_instance, "maximum_marks_external", 0) or 0
            if getattr(exam_skill_instance, "has_internal_marks", False):
                max_internal = getattr(exam_skill_instance, "maximum_marks_internal", 0) or 0

        total_max = max_external + max_internal
        percentage = (marks_obtained / total_max) * 100 if total_max > 0 else None

        # if not percentage:
        #     return

        if exam and exam.category:
            grade = GradeBoundary.objects.filter(
                category=exam.category,
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                is_active=True
            ).first()
        else:
            grade = GradeBoundary.objects.filter(
                category__isnull=True,
                min_percentage__lte=percentage,
                max_percentage__gte=percentage,
                is_active=True
            ).first()

        if grade:
            ExamSkillResult.objects.filter(exam_skill_result_id=exam_skill_result_id).update(
                marks_obtained=marks_obtained,
                percentage=percentage,
                grade=grade,
            )

    except ExamSkillResult.DoesNotExist:
        pass


@shared_task
def compute_section_wise_completion(exam_id, result_student_id):
    exam = Exam.objects.get(exam_id=exam_id)
    result_student = Student.objects.get(student_id=result_student_id)
    students = Student.objects.filter(
        section=result_student.section,
        is_active=True,
        academic_year=exam.academic_year,
    ).exclude(admission_status__admission_status_id=3)

    exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True)
    total_results = 0
    pending_results = 0

    for exam_instance in exam_instances:
        subject_results = ExamResult.objects.filter(
            student__in=students, exam_instance=exam_instance, is_active=True
        )

        ext = exam_instance.has_external_marks
        intl = exam_instance.has_internal_marks
        grade = exam_instance.has_subject_co_scholastic_grade
        enabled_components = sum([bool(ext), bool(intl), bool(grade)])
        total_results += subject_results.count() * enabled_components

        if ext:
            pending_results += subject_results.filter(
                exam_attendance__exam_attendance_status_id=1
            ).filter(Q(external_marks__isnull=True) | Q(external_marks=None)).count()

        if intl:
            pending_results += subject_results.filter(
                Q(internal_marks__isnull=True) | Q(internal_marks=None)
            ).count()

        if grade:
            pending_results += subject_results.filter(
                Q(co_scholastic_grade__isnull=True) | Q(co_scholastic_grade=None)
            ).count()

        if exam_instance.has_subject_skills:
            skill_instances = ExamSubjectSkillInstance.objects.filter(
                exam_instance=exam_instance, is_active=True
            )

            for skill_instance in skill_instances:
                ext = skill_instance.has_external_marks
                intl = skill_instance.has_internal_marks
                grade = skill_instance.has_subject_co_scholastic_grade
                enabled_components = sum([bool(ext), bool(intl), bool(grade)])

                skill_results = ExamSkillResult.objects.filter(
                    exam_result__in=subject_results,
                    skill=skill_instance.subject_skill,
                )

                total_results += skill_results.count() * enabled_components

                if ext:
                    pending_results += skill_results.filter(
                        exam_attendance__exam_attendance_status_id=1
                    ).filter(Q(external_marks__isnull=True) | Q(external_marks=None)).count()

                if intl:
                    pending_results += skill_results.filter(
                        Q(internal_marks__isnull=True) | Q(internal_marks=None)
                    ).count()

                if grade:
                    pending_results += skill_results.filter(
                        Q(co_scholastic_grade__isnull=True) | Q(co_scholastic_grade=None)
                    ).count()

    completed = total_results - pending_results if total_results else 0
    percentage = (completed / total_results * 100) if total_results else 0

    if percentage == 100:
        status = ExamResultStatus.objects.get(id=3)
    elif percentage > 0:
        status = ExamResultStatus.objects.get(id=2)
    else:
        status = ExamResultStatus.objects.get(id=1)

    SectionWiseExamResultStatus.objects.update_or_create(
        academic_year=exam.academic_year,
        branch=result_student.branch,
        section=result_student.section,
        exam=exam,
        defaults={
            'marks_completion_percentage': Decimal(round(percentage, 2)),
            'status': status,
        },
    )

    return percentage
