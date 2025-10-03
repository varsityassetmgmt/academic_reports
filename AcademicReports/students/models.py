from django.db import models
# from exams.models import *
# from branches.models import *
# from reports.models import *
# from users.models import *


class ClassName(models.Model):
    varna_class_id  = models.CharField(max_length=250,null=True,blank=True,unique=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)    
    description = models.TextField(null=True, blank=True)
    class_sequence = models.SmallIntegerField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

class Orientation(models.Model):
    varna_orientation_id  = models.CharField(max_length=250,null=True,blank=True,unique=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    short_code  = models.CharField(max_length=100,null=False,blank=False)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
 
    def __str__(self):
        return self.name


class Gender(models.Model):
    gender_id = models.BigAutoField(primary_key=True)
    varna_gender_id  = models.CharField(max_length=250,null=True,blank=True)
    name = models.CharField(max_length=100,null=False,blank=True,unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class AdmissionStatus(models.Model):
    admission_status_id = models.BigAutoField(primary_key=True)
    admission_status = models.CharField(max_length=250 ,null=False,blank=False,unique=True)
    short_code = models.CharField(max_length=150, null=True,blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.admission_status
    
class Student(models.Model):   
    student_id = models.BigAutoField(primary_key=True, db_index=True)
    varna_student_id  = models.CharField(max_length=250,null=True,blank=True)
    academic_year = models.ForeignKey("branches.AcademicYear", on_delete=models.PROTECT,null=True,blank=True,related_name='student_academic_year')
    SCS_Number = models.CharField(max_length=150, null=False,blank=False,unique=True)
    name = models.CharField(max_length=250,null=False,blank=False)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT, null=True, blank=True, related_name='student_gender')
    admission_status = models.ForeignKey(AdmissionStatus, on_delete=models.PROTECT, null=True, blank=True, related_name='student_admission_status')
    state = models.ForeignKey("branches.State", on_delete=models.PROTECT, null=True, blank=True, related_name='student_state')
    zone  = models.ForeignKey("branches.Zone", on_delete=models.PROTECT, null=True, blank=True, related_name='student_zone')
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, null=True, blank=True, related_name='student_branch')
    orientation = models.ForeignKey(Orientation, on_delete=models.PROTECT, null=True, blank=True, related_name='student_orientation')
    student_class = models.ForeignKey(ClassName, on_delete=models.PROTECT, null=True, blank=True, related_name='student_class_name')    
    section = models.ForeignKey("branches.Section", on_delete=models.PROTECT, null=True, blank=True, related_name='student_section')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.SCS_Number

    class Meta:
        ordering = ['name']  # Default ordering by name
        indexes = [
            models.Index(fields=['SCS_Number'], name='student_scs_number_idx'),
            models.Index(fields=['is_active'], name='student_is_active_idx'),
            models.Index(fields=['branch'], name='student_branch_idx'),
        ]
        
