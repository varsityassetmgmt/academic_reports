# serializers.py
from rest_framework import serializers
from exams.models import StudentExamSummary

# class StudentProgressCardsListForWebsiteSerializer(serializers.ModelSerializer):
#     exam_type = serializers.CharField(source='exam.exam_type.name', read_only=True)
#     exam_name = serializers.CharField(source='exam.name', read_only=True)
#     academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
#     scs_numner = serializers.CharField(source='student.Scs_number', read_only=True)

#     class Meta:
#         model = StudentExamSummary
#         fields = [
#             'students_exam_summary_id',
#             'exam_type',
#             'exam_name',
#             'scs_numner',
#             'exam',
#             'academic_year_name'
#         ]



class StudentProgressCardsListForWebsiteSerializer(serializers.ModelSerializer):
    progress_reports_id = serializers.CharField(source='students_exam_summary_id', read_only=True)
    progress_reports_name = serializers.CharField(source='exam.name', read_only=True)
    academic_year = serializers.CharField(source='academic_year.name', read_only=True)
    scs_numner = serializers.CharField(source='student.Scs_number', read_only=True)

    class Meta:
        model = StudentExamSummary
        fields = [
            'progress_reports_id',
            'progress_reports_name',
            'scs_numner',
            'academic_year'
        ]