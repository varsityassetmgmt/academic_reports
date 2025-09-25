from django.db import models
from django.utils import timezone

from students.models import ClassName, Orientation

# Create your models here.
class AcademicYear(models.Model):
    academic_year_id = models.BigAutoField(primary_key=True)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    name = models.CharField(max_length=150,null=False,blank=False,unique=True)
    is_current_academic_year = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    description = models.TextField(null=True,blank=True)
    def __str__(self):
        return self.name
    
class AcademicDevision(models.Model):
    academic_devision_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length= 250, null=False,blank=False,unique=True)
    classes = models.ManyToManyField(ClassName,blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
#============================ State =================================
class State(models.Model):
    state_id = models.BigAutoField(primary_key=True, db_index=True)
    name =  models.CharField(max_length=250,null=False, blank=False,unique = True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
#============================== ZONE =============================
class Zone(models.Model):
    zone_id = models.BigAutoField(primary_key=True, db_index=True)
    state = models.ForeignKey(State,related_name="zone_state",null=True, blank=True,on_delete=models.PROTECT)     
    name =  models.CharField(max_length=100,null=False, blank=False,unique = True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

#===================== Location ==================================
class Branch(models.Model):
    branch_id = models.BigAutoField(primary_key=True)
    state = models.ForeignKey(State,related_name="branch_state", null=False, blank=False, on_delete=models.PROTECT)
    zone = models.ForeignKey(Zone,related_name="branch_zone", null=False, blank=False, on_delete=models.PROTECT)
    name = models.CharField(max_length=250, null=False, blank=False, unique=True)
    building_code = models.CharField(max_length=200, null=True, blank=True)
    location_incharge = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phonenumber = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    academic_devisions = models.ManyToManyField(AcademicDevision, related_name="branch_acd_dev", blank=True)
    classes =  models.ManyToManyField(ClassName, related_name="branch_classes", blank=True)
    orientations = models.ManyToManyField(Orientation, related_name="branch_orientation", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp field
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated on save

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        indexes = [
            models.Index(fields=['state'], name='branch_state_idx'),
            models.Index(fields=['zone'], name='branch_zone_idx'),
            models.Index(fields=['name'], name='branch_name_idx'),
            models.Index(fields=['is_active'], name='branch_is_active_idx'),
        ]
