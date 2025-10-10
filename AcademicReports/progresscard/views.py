from django.shortcuts import render

# Create your views here.
from django.template import Template, Context
from django.http import HttpResponse
from exams.models import *
from students.models import *
from weasyprint import HTML

def generate_progress_card_pdf(request, student_id, exam_id):

    student = Student.objects.get(pk=student_id)
    exam = Exam.objects.get(pk=exam_id)
    template = exam.progress_card_template

    if not template:
        return HttpResponse("No progress card template assigned to this exam.", status=404)

    exam_results = ExamResult.objects.filter(student=student, exam_instance__exam=exam)
    summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

    context = {
        "student": student,
        "exam": exam,
        "exam_results": exam_results,
        "summary": summary,
        "generated_at": timezone.now(),
    }

    # Load dynamic HTML and CSS from DB
    html_template = Template(template.html_template)
    rendered_html = html_template.render(Context(context))

    if template.css_styles:
        rendered_html = f"<style>{template.css_styles}</style>" + rendered_html

    pdf_file = HTML(string=rendered_html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{student.first_name}_{exam.name}_ProgressCard.pdf"'
    return response
