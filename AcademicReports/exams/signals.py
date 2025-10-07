from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ExamInstance, ExamSubjectSkillInstance

@receiver(post_save, sender=ExamInstance)
def create_or_update_exam_subject_skill_instance(sender, instance, **kwargs):
    # Always fetch the related subject skills properly
    subject_skills = instance.subject_skills.all()
    
    # Fetch all existing skill instances for this exam
    existing_instances = ExamSubjectSkillInstance.objects.filter(exam_instance=instance)

    # If subject_skills flag is turned off — deactivate all skill instances
    if not instance.has_subject_skills:
        existing_instances.update(is_active=False)
        return

    # --- Step 1: Create missing ExamSubjectSkillInstances ---
    for skill in subject_skills:
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

    # --- Step 2: Deactivate instances for removed skills ---
    for existing in existing_instances:
        if existing.subject_skill not in subject_skills:
            existing.is_active = False
            existing.save()


                                                                                           