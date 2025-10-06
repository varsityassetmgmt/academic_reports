from rest_framework import serializers
from .models import *


# ==================== Subject ====================
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


# ==================== SubjectSkill ====================
class SubjectSkillSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SubjectSkill
        fields = '__all__'


# ==================== ExamType ====================
class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'


# ==================== Exam ====================
class ExamSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'


# ==================== ExamInstance ====================
class ExamInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_skill_names = serializers.SerializerMethodField()

    class Meta:
        model = ExamInstance
        fields = '__all__'

    def get_subject_skill_names(self, obj):
        # Get all related subject skill names and join with comma
        return ', '.join(obj.subject_skills.values_list('name', flat=True))


# ==================== Exam Skill Instance ====================
class ExamSubjectSkillInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='exam_instance.subject.name', read_only=True)
    subject_skill_name = serializers.CharField(source='subject_skill.name', read_only=True)

    class Meta:
        model = ExamSubjectSkillInstance
        fields = '__all__'

# ==================== ExamAttendanceStatus ====================
class ExamAttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendanceStatus
        fields = '__all__'


# ==================== GradeBoundary ====================
class GradeBoundarySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeBoundary
        fields = '__all__'


# ==================== ExamResult ====================
class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__'


# ==================== ExamSkillResult ====================
class ExamSkillResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSkillResult
        fields = '__all__'


# ==================== StudentExamSummary ====================
class StudentExamSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamSummary
        fields = '__all__'

# ---------------- Subject ----------------
class SubjectDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['subject_id', 'name', 'label']

    def get_label(self, obj):
        return str(obj)


# ---------------- SubjectSkill ----------------
class SubjectSkillDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = SubjectSkill
        fields = ['id', 'name', 'label']

    def get_label(self, obj):
        return str(obj)


# ---------------- ExamType ----------------
class ExamTypeDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = ExamType
        fields = ['exam_type_id', 'name', 'label']

    def get_label(self, obj):
        return str(obj)


# ---------------- Exam ----------------
class ExamDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['exam_id', 'name', 'label']

    def get_label(self, obj):
        return str(obj)


# ---------------- ExamInstance ----------------
class ExamInstanceDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = ExamInstance
        fields = ['exam_instance_id', 'exam', 'subject', 'label']

    def get_label(self, obj):
        return str(obj)


# ---------------- ExamAttendanceStatus ----------------
class ExamAttendanceStatusDropdownSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = ExamAttendanceStatus
        fields = ['exam_attendance_status_id', 'name', 'short_code', 'label']

    def get_label(self, obj):
        return str(obj)
