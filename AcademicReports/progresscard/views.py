
from django.template import Context
from exams.models import *
from students.models import Student
# from progresscard.utils.pdf import render_template_from_db, html_to_pdf_bytes
# from progresscard.utils.safe_exec import exec_template_script  # optional
from rest_framework import permissions, status
import pdfkit
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone 
from rest_framework.response import Response
from django.template import engines
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from progresscard.models import *
from students.models import *
from exams.models import *

 
class DownloadProgressCardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get("student_id")
        exam_id = request.query_params.get("exam_id")

        if not student_id or not exam_id:
            return Response(
                {"error": "student_id and exam_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Fetch student and exam
        try:
            student = Student.objects.get(pk=student_id)
            exam = Exam.objects.select_related("progress_card_mapping__template").get(pk=exam_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Fetch template mapping
        mapping = getattr(exam, "progress_card_mapping", None)
        if not mapping or not mapping.template:
            return Response({"error": "No progress card template assigned"}, status=status.HTTP_400_BAD_REQUEST)

        template = mapping.template

        # ✅ Fetch exam data
        exam_results = ExamResult.objects.filter(
            student=student, exam_instance__exam=exam
        ).select_related("exam_instance__subject")

        summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

        # ✅ Context
        context = {
            "student": student,
            "exam": exam,
            "exam_results": exam_results,
            "summary": summary,
            "generated_at": timezone.now(),
            # "logo_url": request.build_absolute_uri(static("images/schoolLogo.png")),
        }

        # ✅ Optional custom script
        if template.script:
            try:
                exec(template.script, {}, context)
            except Exception as e:
                context["script_error"] = str(e)

        # ✅ Render HTML
        html = self.render_template_from_db(template.html_template, template.css_styles, context)

        # ✅ Convert to PDF
        pdf_bytes = self.html_to_pdf(html, request)

        filename = f"{student.name}_{exam.name}_ProgressCard.pdf".replace(" ", "_")
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def render_template_from_db(self, html_text, css_text, context):
        """Combine Bootstrap + Fonts + DB Template + Custom CSS"""
        django_engine = engines["django"]

        # html = f"""
        # <!DOCTYPE html>
        # <html lang="en">
        # <head>
        #     <meta charset="UTF-8">
        #     <meta name="viewport" content="width=device-width, initial-scale=1.0">
        #     <title>Progress Report</title>
        #     <!-- Bootstrap -->
        #     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        #     <!-- Fonts -->
        #     <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        #     <style>{css_text or ''}</style>
        # </head>
        # <body>
        #     {html_text}
        # </body>
        # </html>
        # """

        html = f"<style>{css_text or ''}</style>{html_text}"
        

        template = django_engine.from_string(html)
        return template.render(context)

    def html_to_pdf(self, rendered_html, request):
        """Convert HTML string to PDF"""
        base_url = request.build_absolute_uri('/')

        options = {
            "enable-local-file-access": "",
            "page-size": "A4",
            "encoding": "UTF-8",
            "margin-top": "10mm",
            "margin-bottom": "10mm",
            "margin-left": "10mm",
            "margin-right": "10mm",
            "quiet": "",
        }

        # Replace static paths for wkhtmltopdf
        rendered_html = rendered_html.replace('src="/static/', f'src="{base_url}static/')

        # ✅ Safe configuration
        config = None
        if hasattr(settings, "WKHTMLTOPDF_CMD"):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_CMD)

        try:
            return pdfkit.from_string(rendered_html, False, configuration=config, options=options)
        except Exception as e:
            return f"<h3>Error generating PDF: {e}</h3>".encode("utf-8")

