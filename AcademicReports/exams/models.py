

from django.db import models
from django.core.exceptions import ValidationError


class Subject(models.Model):
    subject_id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    academic_devisions = models.ManyToManyField("branches.AcademicDevision",blank=True, related_name='subject_academic_devisions')
    class_names = models.ManyToManyField("students.ClassName",blank=True, related_name='subject_classes')
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True,blank=True)
    display_name = models.CharField(max_length=250,null=True,blank=True)

    def __str__(self):
        return self.name
    
    
class SubjectSkill(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=255)  # Example: Fluency, Application, Basic Concepts
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "name"],
                name="unique_subject_skill_name"
            )
        ]
    def __str__(self):
        return f"{self.subject.name} - {self.name}"
    


class ExamType(models.Model):
    exam_type_id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Exam(models.Model):
    exam_id = models.BigAutoField(primary_key=True)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='exams_exam_type')
    academic_year = models.ForeignKey("branches.AcademicYear",on_delete=models.CASCADE, related_name='exams_academic_year')
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    states = models.ManyToManyField("branches.State",blank=True, related_name='exams_states')
    zones = models.ManyToManyField("branches.Zone",blank=True, related_name='exams_zones')
    branches = models.ManyToManyField("branches.Branch",blank=True, related_name='exams_branches')

    orientations = models.ManyToManyField("students.Orientation", blank=True, related_name='exams_orientations')

    academic_devisions = models.ManyToManyField("branches.AcademicDevision",blank=True, related_name='exam_academic_devisions')
    student_classes = models.ManyToManyField("students.ClassName",blank=True, related_name='exams_classes')
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "academic_year", "exam_type"],
                name="unique_exam_per_year_type"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.exam_type.name})"

class ExamInstance(models.Model):
    exam_instance_id = models.BigAutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_instance_exam')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_instance_subject')    

    # Flags to indicate what kind of results this exam has
    has_external_marks = models.BooleanField(default=False)
    has_internal_marks = models.BooleanField(default=False)
    has_subject_skills = models.BooleanField(default=False)
   
    # Hall ticket related
    date = models.DateField()                              
    exam_start_time = models.TimeField()                   
    exam_end_time = models.TimeField()                 

    maximum_marks_external = models.IntegerField(blank=True,null=True)
    cut_off_marks_external = models.IntegerField(blank=True, null=True)

    maximum_marks_internal = models.IntegerField(blank=True,null=True)
    cut_off_marks_internal = models.IntegerField(blank=True, null=True)

    # Link only selected skills for this exam
    subject_skills = models.ManyToManyField("SubjectSkill", blank=True, related_name="exam_instances")

    is_optional = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # result_types = models.ManyToManyField("ResultType", related_name="exam_instances")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "subject"],
                name="unique_exam_subject_instance"
            )
        ]

    # def clean(self):
    #     # date within exam bounds
    #     # if self.date and not (self.exam.start_date <= self.date <= self.exam.end_date):
    #     #     raise ValidationError("ExamInstance date must be within the parent Exam start_date and end_date.")

    #     # subject_skills belong to subject
    #     if self.pk:
    #         skills_qs = self.subject_skills.all()
    #     else:
    #         # in forms, m2m not available until saved — skip the skills check on unsaved instance
    #         skills_qs = None

    #     if skills_qs is not None:
    #         invalid = skills_qs.exclude(subject=self.subject).exists()
    #         if invalid:
    #             raise ValidationError("All subject_skills must belong to the same subject as this ExamInstance.")
#
    def __str__(self):
        return f"({self.exam.name} - {self.subject.name})"

class ExamAttendanceStatus(models.Model):
    exam_attendance_status_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)   
    short_code = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name 


class GradeBoundary(models.Model):
    grade_boundary_id = models.BigAutoField(primary_key=True)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="grade_bound_exam_type")
    orientation = models.ForeignKey("students.Orientation", on_delete=models.CASCADE, related_name="grade_bound_orientation")
    grade = models.CharField(max_length=10)  # e.g., 'A+', 'A', etc.
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 84.50
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 100.00
    remarks = models.CharField(max_length=100, null=True, blank=True)  # e.g., 'Excellent', 'Good', etc.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-min_percentage']  # Highest to lowest for easier matching
        unique_together = ('exam_type', 'orientation', 'grade')  # Ensure uniqueness for each combination

    def __str__(self):
        return f"{self.grade} ({self.exam_type.name} - {self.orientation.name})"

    @staticmethod
    def get_grade_for_percentage(exam_type, orientation, percentage):
        """
        Returns the grade for a given percentage for a specific exam type and orientation.
        If no matching grade boundary is found, it returns None.
        """
        return GradeBoundary.objects.filter(
            exam_type=exam_type,
            orientation=orientation,
            min_percentage__lte=percentage,
            max_percentage__gte=percentage
        ).first()


class ExamResult(models.Model):
    exam_result_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name='exam_results_student')    
    exam_instance = models.ForeignKey(ExamInstance, on_delete=models.CASCADE, related_name='exam_results_exam_instance')
    exam_attendance = models.ForeignKey(ExamAttendanceStatus, on_delete=models.CASCADE, related_name='exam_results_attendance')
    external_marks = models.IntegerField(null=True, blank=True)     
    internal_marks = models.IntegerField(null=True, blank=True)     
    marks_obtained = models.IntegerField(null=True, blank=True)  # Total marks 
    # percentage = models.IntegerField(null=True, blank=True)  # percentage 
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # grade = models.CharField(max_length=5, null=True, blank=True)

    class_rank = models.IntegerField(null=True, blank=True)  # Class rank
    section_rank = models.IntegerField(null=True, blank=True)  # Section rank
    zone_rank = models.IntegerField(null=True, blank=True)  # New field for zone rank
    state_rank = models.IntegerField(null=True, blank=True)  # New field for state rank
    all_india_rank = models.IntegerField(null=True, blank=True)  # New field for all India rank
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["student", "exam_instance"],
            name="unique_student_exam_instance"
            )
        ]
        # unique_together = ('student', 'exam_instance')
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['exam_instance']),
            models.Index(fields=['marks_obtained']),  # Add this line to index marks_obtained
        ]
    
    def save(self, *args, **kwargs):
        total_max = (self.exam_instance.maximum_marks_external or 0) + (self.exam_instance.maximum_marks_internal or 0)
        obtained = (self.external_marks or 0) + (self.internal_marks or 0)
        self.marks_obtained = obtained
        if total_max > 0:
            self.percentage = (obtained / total_max) * 100
        super().save(*args, **kwargs)


  
    def __str__(self):
        return f"{self.student} - {self.exam_instance.subject.name}"

class ExamSkillResult(models.Model):
    examp_skill_result_id = models.BigAutoField(primary_key=True)
    exam_result = models.ForeignKey(ExamResult, on_delete=models.CASCADE, related_name="skill_results")
    skill = models.ForeignKey(SubjectSkill, on_delete=models.CASCADE, related_name="skill_results")
    value = models.CharField(max_length=150)  
    # e.g. "A", "B", "C" or "Yes"/"No" or "Marks"

    def __str__(self):
        return f"{self.exam_result.student} - {self.skill.name}: {self.value}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam_result", "skill"],
                name="unique_examresult_skill"
            )
        ]

class StudentExamSummary(models.Model):
    students_exam_summary_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name='exam_summary_student')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_summary_exam')
    
    total_subjects_marks = models.IntegerField(default=0)  # Total marks across all subjects
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    overall_grade = models.CharField(max_length=3, null=True, blank=True)  # Overall grade (A+, A, B, etc.)
    overall_remarks = models.CharField(max_length=100, null=True, blank=True)  # Overall remarks (Very Good, Good, etc.)

    # Ranking fields
    section_rank = models.IntegerField(null=True, blank=True)
    class_rank = models.IntegerField(null=True, blank=True)
    zone_rank = models.IntegerField(null=True, blank=True)
    state_rank = models.IntegerField(null=True, blank=True)
    all_india_rank = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default= True)

    # class Meta:
    #     unique_together = ('student', 'exam')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "exam"],
                name="unique_student_exam_summary"
            )
        ]

        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['exam']),
            models.Index(fields=['total_subjects_marks']),  # Add index for total_subject_marks
        ]
    
    def __str__(self):
        return f"Summary for {self.student} in {self.exam.name}"
