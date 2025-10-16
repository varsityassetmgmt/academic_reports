from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from exams.models import *
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from students.models import Student
from django.db.models import Q
from decimal import Decimal

@receiver(m2m_changed, sender=ExamInstance.subject_skills.through)
def sync_exam_subject_skills(sender, instance, action, pk_set, **kwargs):
    """
    Keep ExamSubjectSkillInstance in sync whenever subject_skills M2M is updated.
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Fetch the current subject skills
        current_skills = instance.subject_skills.all()

        # Step 1: Create missing ExamSubjectSkillInstances
        for skill in current_skills:
            obj, created = ExamSubjectSkillInstance.objects.get_or_create(
                exam_instance=instance,
                subject_skill=skill,
                defaults={
                    "created_by": instance.created_by,
                    "updated_by": instance.updated_by,
                },
            )
            if not obj.is_active:
                obj.is_active = True
                obj.save()

        # Step 2: Deactivate instances for removed skills
        existing_instances = ExamSubjectSkillInstance.objects.filter(exam_instance=instance)
        for existing in existing_instances:
            if existing.subject_skill not in current_skills:
                existing.is_active = False
                existing.save()



def update_examresult_skill_totals(exam_result):
    """Recalculate and update the skill totals on the given ExamResult."""
    if not exam_result:
        return

    skill_totals = exam_result.skill_results.aggregate(
        skill_external_sum=Sum('external_marks'),
        skill_internal_sum=Sum('internal_marks'),
        skill_total_sum=Sum('marks_obtained')
    )

    exam_result.skill_external_marks = skill_totals['skill_external_sum'] or 0
    exam_result.skill_internal_marks = skill_totals['skill_internal_sum'] or 0
    exam_result.skill_total_marks = skill_totals['skill_total_sum'] or 0

    exam_result.save(update_fields=[
        'skill_external_marks',
        'skill_internal_marks',
        'skill_total_marks'
    ])


@receiver(post_save, sender=ExamSkillResult)
def update_skill_totals_after_save(sender, instance, **kwargs):
    """Update ExamResult totals when a skill result is created or updated."""
    update_examresult_skill_totals(instance.exam_result)


@receiver(post_delete, sender=ExamSkillResult)
def update_skill_totals_after_delete(sender, instance, **kwargs):
    """Update ExamResult totals when a skill result is deleted."""
    update_examresult_skill_totals(instance.exam_result)


# @receiver(post_save, sender=ExamSkillResult)
# def update_section_wise_marks_completion_percentage(sender, instance, **kwargs):
#     exam_result = instance.exam_result
#     student = exam_result.student
#     exam = exam_result.exam_instance.exam

#     # Active exam instances for this exam
#     exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True)

#     # Active students in the same section
#     students = Student.objects.filter(
#         section=student.section,
#         is_active=True,
#         academic_year=exam.academic_year
#     ).exclude(admission_status__admission_status_id=3)

#     total_results = 0
#     pending_results = 0

#     for exam_instance in exam_instances:
#         subject_results = ExamResult.objects.filter(
#             student__in=students,
#             exam_instance=exam_instance,
#             is_active=True
#         )

#         # --- SUBJECT LEVEL ---
#         external_marks_status = exam_instance.has_external_marks
#         internal_marks_status = exam_instance.has_internal_marks
#         grade_status = exam_instance.has_subject_co_scholastic_grade

#         enabled_components = sum([
#             bool(external_marks_status),
#             bool(internal_marks_status),
#             bool(grade_status)
#         ])

#         total_results += subject_results.count() * enabled_components

#         if external_marks_status:
#             pending_results += subject_results.filter(
#                 Q(external_marks__isnull=True) | Q(external_marks__exact='')
#             ).count()
#         if internal_marks_status:
#             pending_results += subject_results.filter(
#                 Q(internal_marks__isnull=True) | Q(internal_marks__exact='')
#             ).count()
#         if grade_status:
#             pending_results += subject_results.filter(
#                 Q(co_scholastic_grade__isnull=True) | Q(co_scholastic_grade__exact='')
#             ).count()

#         # --- SKILL LEVEL ---
#         if exam_instance.has_subject_skills:
#             skill_instances = ExamSubjectSkillInstance.objects.filter(
#                 exam_instance=exam_instance, is_active=True
#             )

#             for skill_instance in skill_instances:
#                 external_marks_status = skill_instance.has_external_marks
#                 internal_marks_status = skill_instance.has_internal_marks
#                 grade_status = skill_instance.has_subject_co_scholastic_grade

#                 enabled_components = sum([
#                     bool(external_marks_status),
#                     bool(internal_marks_status),
#                     bool(grade_status)
#                 ])

#                 skill_results = ExamSkillResult.objects.filter(
#                     exam_result__in=subject_results,
#                     skill=skill_instance.subject_skill,
#                     is_active=True
#                 )

#                 total_results += skill_results.count() * enabled_components

#                 if external_marks_status:
#                     pending_results += skill_results.filter(
#                         Q(external_marks__isnull=True) | Q(external_marks__exact='')
#                     ).count()
#                 if internal_marks_status:
#                     pending_results += skill_results.filter(
#                         Q(internal_marks__isnull=True) | Q(internal_marks__exact='')
#                     ).count()
#                 if grade_status:
#                     pending_results += skill_results.filter(
#                         Q(co_scholastic_grade__isnull=True) | Q(co_scholastic_grade__exact='')
#                     ).count()

#     # --- COMPUTE PERCENTAGE ---
#     completed_results = total_results - pending_results if total_results else 0
#     completion_percentage = (completed_results / total_results * 100) if total_results else 0

#     # --- UPDATE OR CREATE SECTION-WISE STATUS ---
#     section_status, created = SectionWiseExamResultStatus.objects.update_or_create(
#         academic_year=exam.academic_year,
#         branch=student.branch,
#         section=student.section,
#         exam=exam,
#         defaults={
#             'marks_completion_percentage': Decimal(round(completion_percentage, 2)),
#         }
#     )

    # Optionally log update (for debug)
    # print(f"Updated SectionWiseExamResultStatus: {section_status} -> {completion_percentage:.2f}% completed")

def compute_section_wise_completion(exam, student):
    from exams.models import (
        ExamInstance, ExamResult, ExamSkillResult, ExamSubjectSkillInstance
    )
    from students.models import Student
    from exams.models import SectionWiseExamResultStatus

    exam_instances = ExamInstance.objects.filter(exam=exam, is_active=True)
    students = Student.objects.filter(
        section=student.section,
        is_active=True,
        academic_year=exam.academic_year,
    ).exclude(admission_status__admission_status_id=3)

    total_results = 0
    pending_results = 0

    for exam_instance in exam_instances:
        subject_results = ExamResult.objects.filter(
            student__in=students,
            exam_instance=exam_instance,
            is_active=True,
        )

        # --- SUBJECT LEVEL ---
        ext = exam_instance.has_external_marks
        intl = exam_instance.has_internal_marks
        grade = exam_instance.has_subject_co_scholastic_grade

        enabled_components = sum([bool(ext), bool(intl), bool(grade)])
        total_results += subject_results.count() * enabled_components

        if ext:
            pending_results += subject_results.filter(
                Q(external_marks__isnull=True) | Q(external_marks=None)
            ).count()
        if intl:
            pending_results += subject_results.filter(
                Q(internal_marks__isnull=True) | Q(internal_marks=None)
            ).count()
        if grade:
            pending_results += subject_results.filter(
                Q(co_scholastic_grade__isnull=True) | Q(co_scholastic_grade=None)
            ).count()

        # --- SKILL LEVEL ---
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
                        Q(external_marks__isnull=True) | Q(external_marks=None)
                    ).count()
                if intl:
                    pending_results += skill_results.filter(
                        Q(internal_marks__isnull=True) | Q(internal_marks=None)
                    ).count()
                if grade:
                    pending_results += skill_results.filter(
                        Q(co_scholastic_grade__isnull=True) | Q(co_scholastic_grade=None)
                    ).count()

    # --- COMPUTE ---
    completed = total_results - pending_results if total_results else 0
    percentage = (completed / total_results * 100) if total_results else 0
    if percentage == 100 :
        status = ExamResultStatus.objects.get(id=3)
    elif percentage > 0:
        status = ExamResultStatus.objects.get(id=2)
    else:
        status = ExamResultStatus.objects.get(id=1)

    # --- UPSERT INTO STATUS TABLE ---
    SectionWiseExamResultStatus.objects.update_or_create(
        academic_year=exam.academic_year,
        branch=student.branch,
        section=student.section,
        exam=exam,
        status = status,
        defaults={'marks_completion_percentage': Decimal(round(percentage, 2))},
    )

    return percentage

@receiver(post_save, sender=ExamResult)
def update_section_wise_status_on_exam_result(sender, instance, **kwargs):
    exam = instance.exam_instance.exam
    student = instance.student
    compute_section_wise_completion(exam, student)

@receiver(post_save, sender=ExamSkillResult)
def update_section_wise_status_on_skill_result(sender, instance, **kwargs):
    exam = instance.exam_result.exam_instance.exam
    student = instance.exam_result.student
    compute_section_wise_completion(exam, student)
