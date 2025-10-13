from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from exams.models import *
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver

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

                                                                                           