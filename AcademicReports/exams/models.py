

from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone


class Subject(models.Model):
    subject_id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    academic_devisions = models.ManyToManyField("branches.AcademicDevision",blank=True, related_name='subject_academic_devisions')
    class_names = models.ManyToManyField("students.ClassName",blank=True, related_name='subject_classes')
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True,blank=True)
    display_name = models.CharField(max_length=250,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='subject_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='subject_updated_by',on_delete=models.SET_NULL)

    class Meta:
        indexes = [
                    models.Index(fields=["is_active"]),
                ]

    def __str__(self):
        return self.name
    
    
class SubjectSkill(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=255)  # Example: Fluency, Application, Basic Concepts
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='subject_skill_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='subject_skill_updated_by',on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "name"],
                name="unique_subject_skill_name"
            )
        ]
        indexes = [
                    models.Index(fields=["subject"]),
                    models.Index(fields=["is_active"]),
                ]

    def __str__(self):
        return f"{self.subject.name} - {self.name}"
    


class ExamType(models.Model):
    exam_type_id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_type_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_type_updated_by',on_delete=models.SET_NULL)

    class Meta:
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        return self.name


class Exam(models.Model):
    exam_id = models.BigAutoField(primary_key=True)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='exams_exam_type')
    academic_year = models.ForeignKey("branches.AcademicYear",null=True, blank=True,on_delete=models.CASCADE, related_name='exams_academic_year')
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    states = models.ManyToManyField("branches.State",blank=True, related_name='exams_states')
    zones = models.ManyToManyField("branches.Zone",blank=True, related_name='exams_zones')
    branches = models.ManyToManyField("branches.Branch",blank=True, related_name='exams_branches')

    orientations = models.ManyToManyField("students.Orientation", blank=True, related_name='exams_orientations')

    academic_devisions = models.ManyToManyField("branches.AcademicDevision",blank=True, related_name='exam_academic_devisions')
    student_classes = models.ManyToManyField("students.ClassName",blank=True, related_name='exams_classes')
    is_visible = models.BooleanField(default=False) # Enable this to make the exam visible for marks entry.
    is_progress_card_visible = models.BooleanField(default=False)  # Enable this to allow progress card download for this exam
    is_active = models.BooleanField(default=True)

    marks_entry_expiry_datetime = models.DateTimeField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_updated_by',on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "academic_year", "exam_type"],
                name="unique_exam_per_year_type"
            )
        ]
        indexes = [
                    models.Index(fields=["academic_year"]),
                    models.Index(fields=["exam_type"]),
                    models.Index(fields=["academic_year", "exam_type"]),
                    models.Index(fields=["is_visible"]),
                    models.Index(fields=["is_progress_card_visible"]),
                    models.Index(fields=["is_active"]),                    
                    models.Index(fields=["start_date", "end_date"]),  # range queries
                    # models.Index(fields=["academic_year", "exam_type", "is_active"], name="idx_exam_year_type_active"),
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
    has_subject_co_scholastic_grade = models.BooleanField(default=False)
   
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

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_instance_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_instance_updated_by',on_delete=models.SET_NULL)

    # result_types = models.ManyToManyField("ResultType", related_name="exam_instances")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "subject"],
                name="unique_exam_subject_instance"
            )
        ]
        indexes = [
                    models.Index(fields=["exam"]),
                    models.Index(fields=["subject"]),
                    models.Index(fields=["date"]),
                    models.Index(fields=["is_active"]),
                    models.Index(fields=["has_external_marks"]),
                    models.Index(fields=["has_internal_marks"]),
                    models.Index(fields=["has_subject_skills"]),
                    models.Index(fields=["has_subject_co_scholastic_grade"]),
                    models.Index(fields=["exam", "subject", "is_active"]),
                ]

    def __str__(self):
        return f"({self.exam.name} - {self.subject.name})"


class ExamSubjectSkillInstance(models.Model):
    exam_instance = models.ForeignKey(ExamInstance, on_delete=models.CASCADE, related_name='exam_subject_skills_instance_exam_instance')
    subject_skill = models.ForeignKey(SubjectSkill, on_delete=models.CASCADE, related_name="exam_subject_skill_instance_subject_skill")

    # Flags to indicate what kind of results this exam has
    has_external_marks = models.BooleanField(default=False)
    has_internal_marks = models.BooleanField(default=False)
    has_subject_co_scholastic_grade = models.BooleanField(default=True)

    maximum_marks_external = models.IntegerField(blank=True,null=True)
    cut_off_marks_external = models.IntegerField(blank=True, null=True)

    maximum_marks_internal = models.IntegerField(blank=True,null=True)
    cut_off_marks_internal = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_subject_skill_instance_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='exam_subject_skill_instance_updated_by',on_delete=models.SET_NULL)

    # result_types = models.ManyToManyField("ResultType", related_name="exam_instances")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam_instance", "subject_skill"],
                name="unique_exam_subject_skill_instance"
            )
        ]
        indexes = [
                    models.Index(fields=["exam_instance"]),
                    models.Index(fields=["subject_skill"]),
                    models.Index(fields=["is_active"]),
                    models.Index(fields=["has_external_marks"]),
                    models.Index(fields=["has_internal_marks"]),
                    models.Index(fields=["has_subject_co_scholastic_grade"]),
                ]


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
        # indexes = [
        #             models.Index(fields=["exam_type", "orientation"]),
        #             models.Index(fields=["min_percentage", "max_percentage"]),
        #         ]

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


class CoScholasticGrade(models.Model):
    """
    Master table for skill grading (Co-Scholastic).
    Example:
    A+ → Outstanding
    A  → Excellent
    B+ → Good
    B  → Average
    C  → Satisfactory
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=5, unique=True)  # e.g., A+, A, B+, B, C
    description = models.CharField(max_length=150, blank=True, null=True)  # e.g., Outstanding, Excellent
    point = models.PositiveSmallIntegerField(default=0)  # e.g., 5, 4, 3, etc.
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='co_scholatic_grade_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='co_scholatic_grade_updated_by',on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-point"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["point"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.description or ''}".strip()

class ExamResult(models.Model):
    exam_result_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name='exam_results_student')    
    exam_instance = models.ForeignKey(ExamInstance, on_delete=models.CASCADE, related_name='exam_results_exam_instance')
    exam_attendance = models.ForeignKey(ExamAttendanceStatus, on_delete=models.CASCADE, related_name='exam_results_attendance')

    # --- Academic Marks ---
    external_marks = models.IntegerField(null=True, blank=True)
    internal_marks = models.IntegerField(null=True, blank=True)
    total_marks = models.IntegerField(null=True, blank=True)  # total = external + internal

    co_scholastic_grade = models.ForeignKey(CoScholasticGrade,on_delete=models.PROTECT,null=True,blank = True, related_name="exam_result_co_scholastic_grade")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    skill_external_marks = models.IntegerField(null=True, blank=True)
    skill_internal_marks = models.IntegerField(null=True, blank=True)
    skill_total_marks = models.IntegerField(null=True, blank=True)

    # --- Ranks ---
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
            models.Index(fields=['external_marks']),            
            models.Index(fields=['total_marks']),  # Add this line to index marks_obtained
            models.Index(fields=["exam_instance", "external_marks"]),  # for ranks
            models.Index(fields=["exam_instance", "total_marks"]),  # for ranks
            models.Index(fields=["percentage"]),
            models.Index(fields=["class_rank"]),
            models.Index(fields=["section_rank"]),
            models.Index(fields=["zone_rank"]),
            models.Index(fields=["state_rank"]),
            models.Index(fields=["all_india_rank"]),
            models.Index(fields=["exam_instance", "student"], name="idx_examresult_exam_student"),
            models.Index(fields=["exam_instance", "is_active"], name="idx_examresult_exam_active"),
            models.Index(fields=["student", "is_active"], name="idx_examresult_student_active"),
            models.Index(fields=["exam_instance", "percentage"], name="idx_examresult_exam_percentage"),

        ]
    
    def save(self, *args, **kwargs):
        total_max = (self.exam_instance.maximum_marks_external or 0) + (self.exam_instance.maximum_marks_internal or 0)
        obtained = (self.external_marks or 0) + (self.internal_marks or 0)
        self.total_marks = obtained
        if total_max > 0:
            self.percentage = (obtained / total_max) * 100
        super().save(*args, **kwargs)


  
    def __str__(self):
        return f"{self.student} - {self.exam_instance.subject.name}"
    
# class SkillResultValue(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     name = models.CharField(max_length=50, unique=True)
#     description = models.CharField(max_length=200, blank=True, null=True)

#     def __str__(self):
#         return self.name


class ExamSkillResult(models.Model):
    examp_skill_result_id = models.BigAutoField(primary_key=True)
    exam_result = models.ForeignKey(ExamResult, on_delete=models.CASCADE, related_name="skill_results")
    skill = models.ForeignKey(SubjectSkill, on_delete=models.CASCADE, related_name="skill_results")
    co_scholastic_grade = models.ForeignKey(CoScholasticGrade,on_delete=models.PROTECT,null=True,blank = True, related_name="exam_skill_results")
    # custom_value = models.CharField(max_length=100, blank=True, null=True)

    external_marks = models.IntegerField(null=True, blank=True)     
    internal_marks = models.IntegerField(null=True, blank=True)     
    marks_obtained = models.IntegerField(null=True, blank=True)  # Total marks 

    def __str__(self):
        return f"{self.exam_result.student} - {self.skill.name}: {self.value}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam_result", "skill"],
                name="unique_examresult_skill"
            )
        ]
        indexes = [
                    models.Index(fields=["exam_result"]),
                    models.Index(fields=["skill"]),
                    models.Index(fields=["co_scholastic_grade"]),
                    models.Index(fields=["exam_result", "skill", "co_scholastic_grade"]),
                ]
    def __str__(self):
        return f"{self.exam_result.student} - {self.skill.name}"
    
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
            models.Index(fields=["percentage"]),
            models.Index(fields=["class_rank"]),
            models.Index(fields=["section_rank"]),
            models.Index(fields=["zone_rank"]),
            models.Index(fields=["state_rank"]),
            models.Index(fields=["all_india_rank"]),
            models.Index(fields=['is_active']),     
        ]
    
    def __str__(self):
        return f"Summary for {self.student} in {self.exam.name}"


class ExamResultStatus(models.Model):
    """
    Stores master statuses like:
    NOT_STARTED, IN_PROGRESS, COMPLETED, VERIFIED, FINALIZED
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name



class BranchWiseExamResultStatus(models.Model):
    academic_year = models.ForeignKey("branches.AcademicYear",null=True, blank=True, on_delete=models.PROTECT, related_name="branch_wise_exam_result_status")
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, related_name="branch_wise_exam_result_status")
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="branch_wise_exam_result_status")
    status = models.ForeignKey(ExamResultStatus, on_delete=models.PROTECT, related_name="branch_wise_exam_result_status")

    finalized_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="finalized_branch_exam_result_status")
    finalized_at = models.DateTimeField(null=True, blank=True)

    is_progress_card_downloaded = models.BooleanField(default=False)
    marks_completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    # Marks entry expiry deadline
    marks_entry_expiry_datetime = models.DateTimeField(null=True,blank=True)

    # 👇 Section tracking fields
    total_sections = models.PositiveIntegerField(default=0)
    number_of_sections_completed = models.PositiveIntegerField(default=0)
    number_of_sections_pending = models.PositiveIntegerField(default=0)
    progress_card_pending_sections = models.PositiveIntegerField(default=0)  # 👈 new field
 

    is_visible = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=["academic_year", "branch", "exam"],
                    name="unique_branch_wise_exam_result_status"
                )
            ]
        indexes = [
            models.Index(fields=["academic_year"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_visible"]),
            models.Index(fields=["marks_entry_expiry_datetime"]),
            models.Index(fields=["is_active"]),
            
        ]
        verbose_name = "Branch Wise Exam Result Status"
        verbose_name_plural = "Branch Wise Exams Result Status"

    def __str__(self):
        return f"{self.exam.name} - {self.branch.name} ({self.academic_year.name})"



class SectionWiseExamResultStatus(models.Model):
    
    academic_year = models.ForeignKey("branches.AcademicYear",null=True, blank=True, on_delete=models.PROTECT,related_name="section_exam_result_status")
    branch = models.ForeignKey("branches.Branch",on_delete=models.PROTECT,related_name="section_exam_result_status")
    section = models.ForeignKey("students.Section",on_delete=models.PROTECT,related_name="section_exam_result_status")
    exam = models.ForeignKey(Exam,on_delete=models.PROTECT,related_name="section_exam_result_status")
    status = models.ForeignKey(ExamResultStatus,on_delete=models.PROTECT,related_name="section_exam_result_status")
    finalized_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="finalized_section_exam_result_status")
    finalized_at = models.DateTimeField(null=True, blank=True)

    # Marks completion
    marks_completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    marks_entry_expiry_datetime = models.DateTimeField(null=True, blank=True)
    is_progress_card_downloaded = models.BooleanField(default=False)

    # Visibility & timestamps
    is_visible = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("academic_year", "branch", "section", "exam")
        constraints = [
                models.UniqueConstraint(
                    fields=["academic_year", "branch", "section", "exam"],
                    name="unique_section_wise_exam_result_status"
                )
            ]
        indexes = [
            models.Index(fields=["academic_year"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["section"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_visible"]),
            models.Index(fields=["marks_entry_expiry_datetime"]),
            models.Index(fields=["is_active"]),
        ]
        verbose_name = "Section Exam Results Status"
        verbose_name_plural = "Section Exams Result Status"

    def __str__(self):
        return f"{self.exam.name} - {self.section.name} ({self.branch.name} - {self.academic_year.name})"
