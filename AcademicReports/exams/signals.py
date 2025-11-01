from django.db.models.signals import m2m_changed
from exams.models import *
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models import Q
from exams.models import *
from students.models import Student
from decimal import Decimal
from . import tasks

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


@receiver(post_save, sender=SectionWiseExamResultStatus)
def update_branch_wise_result_status(sender, instance, **kwargs):
    branch_sections = SectionWiseExamResultStatus.objects.filter(
        branch=instance.branch,
        exam=instance.exam,
        academic_year=instance.academic_year,
        is_active=True
    )

    total_sections = branch_sections.count()
    if total_sections == 0:
        return

    # --- Aggregate marks completion percentage ---
    total_percentage = Decimal(0)
    number_of_sections_completed = 0
    number_of_sections_pending = 0

    for sec in branch_sections:
        total_percentage += sec.marks_completion_percentage
        if sec.marks_completion_percentage == 100:
            number_of_sections_completed += 1
        else:
            number_of_sections_pending += 1

    avg_percentage = total_percentage / total_sections if total_sections > 0 else 0

    # --- Determine overall status ---
    if avg_percentage == 100:
        status = ExamResultStatus.objects.get(id=3)
    elif avg_percentage > 0:
        status = ExamResultStatus.objects.get(id=2)
    else:
        status = ExamResultStatus.objects.get(id=1)

    defaults = {
        'marks_completion_percentage': Decimal(round(avg_percentage, 2)),
        'status': status,
        'total_sections': total_sections,
        'number_of_sections_completed': number_of_sections_completed,
        'number_of_sections_pending': number_of_sections_pending,
    }

    # --- If all sections are finalized, finalize branch as well ---
    if branch_sections.filter(status_id=4).count() == total_sections:
        finalized_by = instance.finalized_by
        finalized_at = instance.finalized_at
        defaults.update({
            'status': ExamResultStatus.objects.get(id=4),
            'finalized_by': finalized_by,
            'finalized_at': finalized_at,
        })

    # --- Update or create branch-wise record ---
    BranchWiseExamResultStatus.objects.update_or_create(
        academic_year=instance.academic_year,
        branch=instance.branch,
        exam=instance.exam,
        defaults=defaults,
    )

"""

@receiver(post_save, sender=ExamResult)
def handle_exam_result_post_save(sender, instance, created, **kwargs):
    exam = instance.exam_instance.exam
    student = instance.student
    def run_async_tasks():
        tasks.update_exam_result_grade.delay(instance.exam_result_id)
        tasks.compute_section_wise_completion.delay(exam.exam_id, student.student_id)
    
    transaction.on_commit(run_async_tasks)

@receiver(post_save, sender=ExamSkillResult)
def handle_exam_skill_result_post_save(sender, instance, created, **kwargs):
    exam = instance.exam_result.exam_instance.exam
    student = instance.exam_result.student

    def run_async_tasks():
        tasks.update_exam_skill_result_grade.delay(instance.exam_skill_result_id)
        tasks.compute_section_wise_completion.delay(exam.exam_id, student.student_id)
        
    transaction.on_commit(run_async_tasks)

"""