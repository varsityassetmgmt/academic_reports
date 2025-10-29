# exams/utils/bulk.py
import io, zipfile
from django.http import HttpResponse
from .pdf import render_template_from_db, html_to_pdf_bytes
from progresscard.utils.safe_exec import exec_template_script
from exams.models import *

def generate_bulk_progress_cards_zip(request, exam, students_queryset):
    """
    Returns bytes of a ZIP file containing PDFs for provided students.
    """
    mapping = getattr(exam, "progress_card_mapping", None)
    if not mapping or not mapping.template:
        raise ValueError("No template assigned to exam")
    template = mapping.template

    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for student in students_queryset:
            # fetch per-student data
            exam_results = exam.examinstance_set.model.objects.none()  # placeholder
            # You should fetch ExamResult for student
            
            exam_results = ExamResult.objects.filter(student=student, exam_instance__exam=exam).select_related(
                "exam_instance__subject", "co_scholastic_grade"
            )
            summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()
            context = {"student": student, "exam": exam, "exam_results": exam_results, "summary": summary}
            # optional script
            if template.script:
                
                context = exec_template_script(template.script, context)
            rendered_html = render_template_from_db(template.html_template, template.css_styles, context, request=request)
            pdf_bytes = html_to_pdf_bytes(rendered_html, request=request)
            filename = f"{student.first_name}_{student.last_name}_{exam.name}.pdf".replace(" ", "_")
            zf.writestr(filename, pdf_bytes)
    mem_zip.seek(0)
    return mem_zip.getvalue()
