 
from django.db import models
from django.core.exceptions import ValidationError


class Subject(models.Model):
    subject_id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    class_names = models.ManyToManyField("students.ClassName",blank=True, related_name='subject_classes')
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True,blank=True)
    def __str__(self):
        return self.name
    
    
class SubjectSkill(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=255)  # Example: Fluency, Application, Basic Concepts
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("subject", "name")

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
    orientations = models.ManyToManyField("students.Orientation", blank=True, related_name='exams_orientations')
    student_classes = models.ManyToManyField("students.ClassName",blank=True, related_name='exams_classes')
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.exam_type.name})"

class ExamInstance(models.Model):
    exam_instance_id = models.BigAutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_instance_exam')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_instance_subject')    
    has_internal_marks = models.BooleanField(default=False)
    date = models.DateField()                               # this is for Halltickets Genaration
    exam_start_time = models.TimeField()                    # this is for Halltickets Genaration
    exam_end_time = models.TimeField()                      # this is for Halltickets Genaration
    maximum_marks_external = models.IntegerField(blank=True,null=True)
    maximum_marks_internal = models.IntegerField(blank=True,null=True)
    is_optional = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"({self.exam.name} - {self.subject.name})"

class ExamAttendanceStatus(models.Model):
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)   
    short_code = models.CharField(max_length=100,null=False,blank=False) 
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name 


class GradeBoundary(models.Model):
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
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name='exam_results_student')    
    exam_instance = models.ForeignKey(ExamInstance, on_delete=models.CASCADE, related_name='exam_results_exam_instance')
    exam_attendance = models.ForeignKey(ExamAttendanceStatus, on_delete=models.CASCADE, related_name='exam_results_attendance')
    external_marks = models.IntegerField(null=True, blank=True)     
    internal_marks = models.IntegerField(null=True, blank=True)     
    marks_obtained = models.IntegerField(null=True, blank=True)  # Total marks 
    percentage = models.IntegerField(null=True, blank=True)  # percentage 
    class_rank = models.IntegerField(null=True, blank=True)  # Class rank
    section_rank = models.IntegerField(null=True, blank=True)  # Section rank
    zone_rank = models.IntegerField(null=True, blank=True)  # New field for zone rank
    state_rank = models.IntegerField(null=True, blank=True)  # New field for state rank
    all_india_rank = models.IntegerField(null=True, blank=True)  # New field for all India rank
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'exam_instance')
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['exam_instance']),
            models.Index(fields=['marks_obtained']),  # Add this line to index marks_obtained
        ]

  
    def __str__(self):
        return f"{self.student} - {self.exam_instance.subject.name}"


class StudentExamSummary(models.Model):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name='exam_summary_student')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_summary_exam')
    
    total_subjects_marks = models.IntegerField(default=0)  # Total marks across all subjects
    percentage = models.IntegerField(null=True, blank=True)  # percentage
    overall_grade = models.CharField(max_length=3, null=True, blank=True)  # Overall grade (A+, A, B, etc.)
    overall_remarks = models.CharField(max_length=100, null=True, blank=True)  # Overall remarks (Very Good, Good, etc.)

    # Ranking fields
    section_rank = models.IntegerField(null=True, blank=True)
    class_rank = models.IntegerField(null=True, blank=True)
    zone_rank = models.IntegerField(null=True, blank=True)
    state_rank = models.IntegerField(null=True, blank=True)
    all_india_rank = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default= True)

    class Meta:
        unique_together = ('student', 'exam')
        
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['exam']),
            models.Index(fields=['total_subjects_marks']),  # Add index for total_subject_marks
        ]

    def __str__(self):
        return f"Summary for {self.student} in {self.exam.name}"