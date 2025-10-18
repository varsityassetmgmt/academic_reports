
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.template import Context
from exams.models import *
from students.models import Student
from progresscard.utils.pdf import render_template_from_db, html_to_pdf_bytes
from progresscard.utils.safe_exec import exec_template_script  # optional
from rest_framework.response import Response
from rest_framework import permissions, status

# class DownloadProgressCardAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         student_id = request.query_params.get("student_id")
#         exam_id = request.query_params.get("exam_id")
#         if not student_id or not exam_id:
#             return Response({"student_id and exam_id required"},status=status.HTTP_400_BAD_REQUEST)

#         try:
#             student = Student.objects.get(pk=student_id)
#             exam = Exam.objects.select_related("progress_card_mapping__template").get(pk=exam_id)
#         except Student.DoesNotExist:
#             return Response({"Student not found"},status=status.HTTP_400_BAD_REQUEST)
#         except Exam.DoesNotExist:
#             return Response({"Exam not found"},status=status.HTTP_400_BAD_REQUEST)
#         mapping = getattr(exam, "progress_card_mapping", None)
#         if not mapping or not mapping.template:
#             return Response({"No template assigned"},status=status.HTTP_400_BAD_REQUEST)
#         template = mapping.template
#         exam_results = ExamResult.objects.filter(student=student, exam_instance__exam=exam).select_related(
#             "exam_instance__subject", "co_scholastic_grade"
#         )
#         summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

#         context = {
#             "student": student,
#             "exam": exam,
#             "exam_results": exam_results,
#             "summary": summary,
#             "generated_at": timezone.now(),
#         }

#         # optional script execution
#         if getattr(template, "script", None):
#             try:
#                 context = exec_template_script(template.script, context)
#             except Exception as e:
#                 context["script_error"] = str(e)

#         rendered_html = render_template_from_db(template.html_template,template.css_styles,context,request=request)
#         pdf_bytes = html_to_pdf_bytes(rendered_html, request=request)

#         filename = f"{student.name}_{exam.name}_ProgressCard.pdf".replace(" ", "_")
#         response = HttpResponse(pdf_bytes, content_type="application/pdf")
#         response["Content-Disposition"] = f'attachment; filename="{filename}"'
#         return response












# class DownloadProgressCardAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         student_id = request.query_params.get("student_id")
#         exam_id = request.query_params.get("exam_id")

#         if not student_id or not exam_id:
#             return Response(
#                 {"error": "student_id and exam_id are required"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Fetch student and exam safely
#         try:
#             student = Student.objects.get(pk=student_id)
#             exam = Exam.objects.select_related("progress_card_mapping__template").get(pk=exam_id)
#         except Student.DoesNotExist:
#             return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exam.DoesNotExist:
#             return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Check mapping
#         mapping = getattr(exam, "progress_card_mapping", None)
#         if not mapping or not mapping.template:
#             return Response({"error": "No progress card template assigned"}, status=status.HTTP_400_BAD_REQUEST)

#         template = mapping.template

#         # Get exam results and summary
#         exam_results = ExamResult.objects.filter(
#             student=student, exam_instance__exam=exam
#         ).select_related("exam_instance__subject", "co_scholastic_grade")

#         summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

#         context = {
#             "student": student,
#             "exam": exam,
#             "exam_results": exam_results,
#             "summary": summary,
#             "generated_at": timezone.now(),
#         }

#         # Optional custom Python script execution
#         if getattr(template, "script", None):
#             try:
#                 context = exec_template_script(template.script, context)
#             except Exception as e:
#                 context["script_error"] = str(e)

#         # Render and generate PDF
#         rendered_html = render_template_from_db(template.html_template, template.css_styles, context, request)
#         pdf_bytes = html_to_pdf_bytes(rendered_html, request)

#         filename = f"{student.name}_{exam.name}_ProgressCard.pdf".replace(" ", "_")

#         response = HttpResponse(pdf_bytes, content_type="application/pdf")
#         response["Content-Disposition"] = f'attachment; filename="{filename}"'
#         return response


import pdfkit
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# from .models import Student, Exam, ExamResult, StudentExamSummary

# from .utils import exec_template_script, render_template_from_db  # keep if used

import pdfkit
from django.template import engines
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import ExamProgressCardTemplate, ExamProgressCardMapping
from students.models import Student
from exams.models import Exam, ExamResult, StudentExamSummary


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

        # ✅ Fetch mapping and template
        mapping = getattr(exam, "progress_card_mapping", None)
        if not mapping or not mapping.template:
            return Response({"error": "No progress card template assigned"}, status=status.HTTP_400_BAD_REQUEST)

        template = mapping.template

        # ✅ Fetch results
        exam_results = ExamResult.objects.filter(
            student=student, exam_instance__exam=exam
        ).select_related("exam_instance__subject", "co_scholastic_grade")

        summary = StudentExamSummary.objects.filter(student=student, exam=exam).first()

        # ✅ Context
        context = {
            "student": student,
            "exam": exam,
            "exam_results": exam_results,
            "summary": summary,
            "generated_at": timezone.now(),
            # "logo_url": request.build_absolute_uri("/static/images/schoolLogo.png"),
            "css_styles": template.css_styles or "",
        }

        # ✅ Optional custom script
        if template.script:
            try:
                exec(template.script, {}, context)
            except Exception as e:
                context["script_error"] = str(e)

        # ✅ Render from DB
        html = self.render_template_from_db(template.html_template, template.css_styles, context)

        # ✅ Convert to PDF
        pdf_bytes = self.html_to_pdf(html)

        filename = f"{student.name}_{exam.name}_ProgressCard.pdf".replace(" ", "_")

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    # def render_template_from_db(self, html_text, css_text, context):
    #     """Render template + CSS directly from DB fields."""
    #     django_engine = engines["django"]
    #     html = f"<style>{css_text or ''}</style>{html_text}
    #     </body>
    #     </html>
    #     """
    #     template = django_engine.from_string(html)
    #     return template.render(context)

    # def html_to_pdf(self, rendered_html):
    #     """Generate PDF from rendered HTML using pdfkit."""
    #     options = {
    #         "enable-local-file-access": "",
    #         "page-size": "A4",
    #         "encoding": "UTF-8",
    #         "margin-top": "10mm",
    #         "margin-bottom": "10mm",
    #         "margin-left": "10mm",
    #         "margin-right": "10mm",
    #     }

    #     config = None
    #     from django.conf import settings
    #     if hasattr(settings, "WKHTMLTOPDF_CMD"):
    #         config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_CMD)

    #     return pdfkit.from_string(rendered_html, False, configuration=config, options=options)




 
# from django.http import HttpResponse
# from .utils.bulk import generate_bulk_progress_cards_zip
# from students.models import Section  # adjust according to your models

# class DownloadBulkProgressCardsAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         exam_id = request.query_params.get("exam_id")
#         section_id = request.query_params.get("section_id")
#         if not exam_id or not section_id:
#             return HttpResponse("exam_id and section_id required", status=400)
#         try:
#             exam = Exam.objects.get(pk=exam_id)
#             section = Section.objects.get(pk=section_id)
#         except Exception:
#             return HttpResponse("Invalid ids", status=404)

#         students = section.student_set.filter(is_active=True)  # adjust relation
#         zip_bytes = generate_bulk_progress_cards_zip(request, exam, students)

#         response = HttpResponse(zip_bytes, content_type="application/zip")
#         response["Content-Disposition"] = f'attachment; filename="progress_cards_{exam_id}_{section.name}.zip"'
#         return response


# your_app/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.utils import timezone

from exams.models import *
from students.models import *
from progresscard.models import *  
from progresscard.utils.pdf import render_template_from_db, html_to_pdf_bytes
from django.templatetags.static import static
 

 


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
            "logo_url": request.build_absolute_uri(static("images/schoolLogo.png")),
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

