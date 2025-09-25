from django.db import models

# Create your models here.
class ClassName(models.Model):
    class_name_id = models.BigAutoField(primary_key=True)
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
    orientation_id = models.BigAutoField(primary_key=True, db_index=True)
    varna_orientation_id  = models.CharField(max_length=250,null=True,blank=True,unique=True)
    name = models.CharField(max_length=250,null=False,blank=False,unique=True)
    short_code  = models.CharField(max_length=100,null=False,blank=False)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
 
    def __str__(self):
        return self.name