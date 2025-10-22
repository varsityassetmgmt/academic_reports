
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
import io
import zipfile
from django.conf import settings

 
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






class BulkProgressCardDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        exam_id = request.query_params.get("exam_id")
        student_ids = request.query_params.getlist("student_ids[]") or request.query_params.get("student_ids")

        if not exam_id or not student_ids:
            return Response(
                {"error": "exam_id and student_ids[] are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(student_ids, str):
            student_ids = student_ids.split(",")

        # ✅ Get exam & template
        try:
            exam = Exam.objects.select_related("progress_card_mapping__template").get(pk=exam_id)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

        mapping = getattr(exam, "progress_card_mapping", None)
        if not mapping or not mapping.template:
            return Response({"error": "No progress card template assigned"}, status=status.HTTP_400_BAD_REQUEST)

        template = mapping.template
        django_engine = engines["django"]

        # ✅ Prepare ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for student in Student.objects.filter(pk__in=student_ids):
                context = self.get_context(student, exam)
                html = self.render_template(django_engine, template.html_template, template.css_styles, context)
                pdf_bytes = self.html_to_pdf(html, request)

                filename = f"{student.name}_{exam.name}_ProgressCard.pdf".replace(" ", "_")
                zip_file.writestr(filename, pdf_bytes)

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="ProgressCards_{exam.name}.zip"'
        return response

    def get_context(self, student, exam):
        exam_results = ExamResult.objects.filter(
            student=student, exam_instance__exam=exam
        ).select_related("exam_instance__subject")

        summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

        return {
            "student": student,
            "exam": exam,
            "exam_results": exam_results,
            "summary": summary,
            "generated_at": timezone.now(),
        }

    def render_template(self, engine, html_text, css_text, context):
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Progress Report</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>{css_text or ''}</style>
        </head>
        <body>
            {html_text}
        </body>
        </html>
        """
        template = engine.from_string(html)
        return template.render(context)

    def html_to_pdf(self, html, request):
        base_url = request.build_absolute_uri("/")
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

        html = html.replace('src="/static/', f'src="{base_url}static/')
        config = None
        if hasattr(settings, "WKHTMLTOPDF_CMD"):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_CMD)

        return pdfkit.from_string(html, False, configuration=config, options=options)




import io
import pdfkit
from PyPDF2 import PdfMerger
from django.http import HttpResponse
from django.template import engines
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# from .models import Student, Exam, ExamResult, StudentExamSummary





from django.http import HttpResponse
from django.template import engines
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from io import BytesIO
from PyPDF2 import PdfMerger
import pdfkit

class New2BulkProgressCardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 🔹 Get student_ids and exam_id from query params
        student_ids_param = request.query_params.get("student_ids")
        exam_id = request.query_params.get("exam_id")

        if not student_ids_param or not exam_id:
            return Response(
                {"error": "student_ids and exam_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_ids = [int(s.strip()) for s in student_ids_param.split(",") if s.strip()]
        except ValueError:
            return Response({"error": "Invalid student_ids"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Fetch exam and its template mapping
        try:
            exam = Exam.objects.select_related("progress_card_mapping__template").get(pk=exam_id)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

        mapping = getattr(exam, "progress_card_mapping", None)
        if not mapping or not mapping.template:
            return Response({"error": "No progress card template assigned"}, status=status.HTTP_400_BAD_REQUEST)

        template = mapping.template

        # 🔹 Initialize PDF merger
        merger = PdfMerger()

        # 🔹 Loop through each student and generate PDF
        students = Student.objects.filter(pk__in=student_ids)
        if not students.exists():
            return Response({"error": "No valid students found"}, status=status.HTTP_404_NOT_FOUND)

        for student in students:
            pdf_data = self.generate_student_pdf(request, student, exam, template)
            if pdf_data:
                merger.append(BytesIO(pdf_data))

        # 🔹 Merge all student PDFs into one
        merged_buffer = BytesIO()
        merger.write(merged_buffer)
        merger.close()
        merged_buffer.seek(0)

        filename = f"{exam.name}_Bulk_ProgressCards.pdf".replace(" ", "_")
        response = HttpResponse(merged_buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def generate_student_pdf(self, request, student, exam, template):
        """Generate a single student's PDF and return its bytes."""
        exam_results = ExamResult.objects.filter(
            student=student, exam_instance__exam=exam
        ).select_related("exam_instance__subject")

        summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

        context = {
            "student": student,
            "exam": exam,
            "exam_results": exam_results,
            "summary": summary,
            "generated_at": timezone.now(),
        }

        # ✅ Execute optional script (stored in DB)
        if template.script:
            try:
                exec(template.script, {}, context)
            except Exception as e:
                context["script_error"] = str(e)

        # ✅ Render HTML using stored DB template
        html = self.render_template_from_db(template.html_template, template.css_styles, context)

        # ✅ Convert HTML to PDF bytes
        pdf_bytes = self.html_to_pdf(html, request)
        return pdf_bytes

    def render_template_from_db(self, html_text, css_text, context):
        """Combine DB template HTML + CSS"""
        django_engine = engines["django"]
        html = f"<style>{css_text or ''}</style>{html_text}"
        template = django_engine.from_string(html)
        return template.render(context)

    def html_to_pdf(self, rendered_html, request):
        """Convert rendered HTML string to PDF bytes using pdfkit"""
        base_url = request.build_absolute_uri("/")
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

  
        rendered_html = rendered_html.replace('src="/static/', f'src="{base_url}static/')

        config = None
        if hasattr(settings, "WKHTMLTOPDF_CMD"):
            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_CMD)

        try:
            return pdfkit.from_string(rendered_html, False, configuration=config, options=options)
        except Exception as e:
            print("PDF generation error:", e)
            return None
