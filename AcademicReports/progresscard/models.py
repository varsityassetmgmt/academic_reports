from django.db import models

# Create your models here.
class ExamProgressCardTemplate(models.Model):
    template_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255,unique=True)  # e.g., “Midterm Template with Attendance”
    description = models.TextField(null=True, blank=True)
    
    # Store the HTML content (with variables like {{ student.name }}, {{ exam.name }}, etc.)
    html_template = models.TextField()
    
    # Optional CSS (if you want to separate styles)
    css_styles = models.TextField(blank=True, null=True)
    
    # Optionally store a small JS snippet or formula logic (optional)
    script = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
