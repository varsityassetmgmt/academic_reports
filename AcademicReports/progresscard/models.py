from django.db import models
from django.conf import settings

# Create your models here.
class ExamProgressCardTemplate(models.Model):
    template_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,unique=True) 
    description = models.TextField(null=True, blank=True)
    html_template = models.TextField(blank=True, null=True)
    css_styles = models.TextField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='progress_card_temp_created_by',on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name='progress_card_temp_updated_by',on_delete=models.SET_NULL)


    def __str__(self):
        return self.name


class ExamProgressCardMapping(models.Model):
    exam = models.OneToOneField("exams.Exam",on_delete=models.PROTECT,related_name="progress_card_mapping")
    template = models.ForeignKey(ExamProgressCardTemplate,on_delete=models.PROTECT,related_name="exam_mappings")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True,related_name="progress_card_mapping_created_by",on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True,related_name="progress_card_mapping_updated_by",on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Exam Progress Card Mapping"
        verbose_name_plural = "Exam Progress Card Mappings"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["template"]),
        ]

    def __str__(self):
        return f"{self.exam.name} → {self.template.name}"