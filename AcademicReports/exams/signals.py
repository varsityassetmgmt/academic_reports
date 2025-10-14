from django.db.models.signals import m2m_changed
from exams.models import *
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models import Q
from exams.models import *

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



# def update_examresult_skill_totals(exam_result):
#     """Recalculate and update the skill totals on the given ExamResult."""
#     if not exam_result:
#         return

#     skill_totals = exam_result.skill_results.aggregate(
#         skill_external_sum=Sum('external_marks'),
#         skill_internal_sum=Sum('internal_marks'),
#         skill_total_sum=Sum('marks_obtained')
#     )

#     exam_result.skill_external_marks = skill_totals['skill_external_sum'] or 0
#     exam_result.skill_internal_marks = skill_totals['skill_internal_sum'] or 0
#     exam_result.skill_total_marks = skill_totals['skill_total_sum'] or 0

#     exam_result.save(update_fields=[
#         'skill_external_marks',
#         'skill_internal_marks',
#         'skill_total_marks'
#     ])


# @receiver(post_save, sender=ExamSkillResult)
# def update_skill_totals_after_save(sender, instance, **kwargs):
#     """Update ExamResult totals when a skill result is created or updated."""
#     update_examresult_skill_totals(instance.exam_result)


# @receiver(post_delete, sender=ExamSkillResult)
# def update_skill_totals_after_delete(sender, instance, **kwargs):
#     """Update ExamResult totals when a skill result is deleted."""
#     update_examresult_skill_totals(instance.exam_result)

                                                                                           





# def update_section_marks_completion(exam_result):
#     """Recalculate marks completion percentage for that section & exam."""
#     if not exam_result or not exam_result.exam_instance:
#         return

#     exam_instance = exam_result.exam_instance
#     exam = exam_instance.exam
#     student = exam_result.student
#     section = getattr(student, "section", None)
#     branch = getattr(student, "branch", None)
#     academic_year = getattr(student, "academic_year", None)

#     if not section or not branch or not academic_year or not exam:
#         return

#     # Total students in the section for this exam
#     total_students = ExamResult.objects.filter(
#         exam_instance__exam=exam,
#         student__section=section,
#         student__branch=branch,
#         is_active=True
#     ).values('student').distinct().count()

#     if total_students == 0:
#         return

#     # Students with any marks entered (academic or skill)
#     completed_students = ExamResult.objects.filter(
#         exam_instance__exam=exam,
#         student__section=section,
#         student__branch=branch,
#         is_active=True
#     ).filter(
#         Q(external_marks__isnull=False) |
#         Q(internal_marks__isnull=False) |
#         Q(skill_total_marks__isnull=False)
#     ).values('student').distinct().count()

#     completion_percentage = round((completed_students / total_students) * 100, 2)

#     # Update or create SectionWiseExamResultStatus
#     SectionWiseExamResultStatus.objects.update_or_create(
#         academic_year=academic_year,
#         branch=branch,
#         section=section,
#         exam=exam,
#         defaults={'marks_completion_percentage': completion_percentage}
#     )


# # 🔔 Combined signals for create/update/delete
# @receiver([post_save, post_delete], sender=ExamResult)
# def update_completion_on_examresult(sender, instance, **kwargs):
#     update_section_marks_completion(instance)


# @receiver([post_save, post_delete], sender=ExamSkillResult)
# def update_completion_on_skillresult(sender, instance, **kwargs):
#     update_section_marks_completion(instance.exam_result)
