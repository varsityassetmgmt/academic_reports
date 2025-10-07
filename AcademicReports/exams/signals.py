from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import ExamInstance, ExamSubjectSkillInstance

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



                                                                                           