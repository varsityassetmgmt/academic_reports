from django.db.models.signals import m2m_changed
from exams.models import *
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models import Q
from exams.models import *
from students.models import Student
from decimal import Decimal

@receiver(m2m_changed, sender=ExamInstance.subject_skills.through)
def sync_exam_subject_skills(sender, instance, action, pk_set, **kwargs):
    # if action in ['post_add', 'post_remove', 'post_clear']:
        # Fetch current subject skills
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

        # Step 3: Handle has_subject_skills = False
        if not instance.has_subject_skills:
            ExamSubjectSkillInstance.objects.filter(exam_instance=instance).update(is_active=False)




# @receiver(m2m_changed, sender=ExamInstance.subject_skills.through)
# def sync_exam_subject_skills(sender, instance, action, pk_set, **kwargs):
#     """
#     Keep ExamSubjectSkillInstance in sync whenever subject_skills M2M is updated.
#     """
#     if action in ['post_add', 'post_remove', 'post_clear']:
#         # Fetch the current subject skills
#         current_skills = instance.subject_skills.all()

#         # Step 1: Create missing ExamSubjectSkillInstances
#         for skill in current_skills:
#             obj, created = ExamSubjectSkillInstance.objects.get_or_create(
#                 exam_instance=instance,
#                 subject_skill=skill,
#                 defaults={
#                     "created_by": instance.created_by,
#                     "updated_by": instance.updated_by,
#                 },
#             )
#             if not obj.is_active:
#                 obj.is_active = True
#                 obj.save()

#         # Step 2: Deactivate instances for removed skills
#         existing_instances = ExamSubjectSkillInstance.objects.filter(exam_instance=instance)
#         for existing in existing_instances:
#             if existing.subject_skill not in current_skills:
#                 existing.is_active = False
#                 existing.save()



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
            # Pending only if attended and marks missing
            pending_results += subject_results.filter(
                exam_attendance__exam_attendance_status_id=1
            ).filter(
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
                        exam_attendance__exam_attendance_status_id=1
                    ).filter(
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

    # --- STATUS ASSIGN ---
    if percentage == 100:
        status = ExamResultStatus.objects.get(id=3)
    elif percentage > 0:
        status = ExamResultStatus.objects.get(id=2)
    else:
        status = ExamResultStatus.objects.get(id=1)

    # --- UPSERT ---
    SectionWiseExamResultStatus.objects.update_or_create(
        academic_year=exam.academic_year,
        branch=student.branch,
        section=student.section,
        exam=exam,
        defaults={
            'marks_completion_percentage': Decimal(round(percentage, 2)),
            'status': status,
        },
    )

    return percentage
#

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
