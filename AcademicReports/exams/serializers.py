from rest_framework import serializers
from .models import *


# ==================== Subject ====================
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is')


# ==================== SubjectSkill ====================
class SubjectSkillSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SubjectSkill
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active')
 
# ==================== ExamType ====================
class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active')

# ==================== Exam ====================
class ExamSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    marks_entry_expiry_datetime_display = serializers.DateTimeField(source='marks_entry_expiry_datetime', format="%Y-%m-%d %H:%M:%S", read_only = True )

    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active', 'is_visible', 'is_progress_card_visible', 'exam_status')

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError("End date cannot be earlier than start date.")

        return data

# ==================== ExamInstance ====================
class ExamInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_skill_names = serializers.SerializerMethodField()

    class Meta:
        model = ExamInstance
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active')

    def get_subject_skill_names(self, obj):
        # Get all related subject skill names and join with comma
        return ', '.join(obj.subject_skills.values_list('name', flat=True))
    
    def validate(self, data):
        exam = data.get('exam')
        subject = data.get('subject')
        start_time = data.get('exam_start_time')
        end_time = data.get('exam_end_time')
        subject_skills = data.get('subject_skills', [])

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("Exam end time must be later than start time.")

        # Optional: ensure subject belongs to same academic division / class as exam
        if exam and subject:
            exam_classes = exam.student_classes.all()
            subject_classes = subject.class_names.all()
            if exam_classes.exists() and subject_classes.exists():
                if not any(cls in subject_classes for cls in exam_classes):
                    raise serializers.ValidationError("Selected subject does not belong to any of the exam's classes.")
                
        for skill in subject_skills:
            if skill.subject != subject:
                raise serializers.ValidationError(
                    f"Skill '{skill.name}' does not belong to the selected subject '{subject.name}'."
                )
            
        return data


# ==================== Exam Skill Instance ====================
class ExamSubjectSkillInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='exam_instance.subject.name', read_only=True)
    subject_skill_name = serializers.CharField(source='subject_skill.name', read_only=True)

    class Meta:
        model = ExamSubjectSkillInstance
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'subject_skill', 'exam_instance', 'is_active')

    def validate(self, data):
        exam_instance = data.get('exam_instance')
        subject_skill = data.get('subject_skill')

        if exam_instance and subject_skill:
            # Check that skill actually belongs to the same subject as the exam instance
            if subject_skill.subject != exam_instance.subject:
                raise serializers.ValidationError("Selected skill does not belong to the exam's subject.")
        return data

# ==================== ExamAttendanceStatus ====================
class ExamAttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendanceStatus
        fields = '__all__'
        read_only_fields = ('is_active')


# ==================== GradeBoundary ====================
class GradeBoundarySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeBoundary
        fields = '__all__'
        read_only_fields = ('is_active')


# ==================== ExamResult ====================
class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__'
        read_only_fields = ('is_active')


# ==================== ExamSkillResult ====================
class ExamSkillResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSkillResult
        fields = '__all__'
        read_only_fields = ('is_active')


# ==================== StudentExamSummary ====================
class StudentExamSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamSummary
        fields = '__all__'
        read_only_fields = ('is_active')

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

# ---------------- ExamAttendanceStatus ----------------
class BranchWiseExamResultStatusSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    finalized_by_username = serializers.CharField(source='finalized_by.username', read_only=True)
    marks_entry_expiry_datetime_display = serializers.DateTimeField(source='marks_entry_expiry_datetime', format="%Y-%m-%d %H:%M:%S", read_only = True )
    finalized_at_display = serializers.DateTimeField(source='finalized_at', format="%Y-%m-%d %H:%M:%S", read_only = True )

    class Meta:
        model = BranchWiseExamResultStatus
        fields = [
            'id',
            'academic_year',
            'academic_year_name',
            'branch',
            'branch_name',
            'exam',
            'exam_name',
            'status',
            'status_name',
            'finalized_at',
            'finalized_at_display',
            'finalized_by_username',
            'is_progress_card_downloaded',
            'marks_completion_percentage',
            'marks_entry_expiry_datetime',
            'marks_entry_expiry_datetime_display',
            'total_sections',
            'number_of_sections_completed',
            'number_of_sections_pending',
            'progress_card_pending_sections',
            'is_visible',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'academic_year',
            'branch',
            'exam',
            'status',
            'is_progress_card_downloaded',
            'marks_completion_percentage',
            'total_sections',
            'number_of_sections_completed',
            'number_of_sections_pending',
            'progress_card_pending_sections',
            'is_visible',
            'updated_at',
            'finalized_at',
        ]

class SectionWiseExamResultStatusSerializer(serializers.ModelSerializer):
    # Readable names for related fields
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    finalized_by_username = serializers.CharField(source='finalized_by.username', read_only=True)
    finalized_at_display = serializers.DateTimeField(source='finalized_at', format="%Y-%m-%d %H:%M:%S", read_only = True )
    marks_entry_expiry_datetime_display = serializers.DateTimeField(source='marks_entry_expiry_datetime', format="%Y-%m-%d %H:%M:%S", read_only = True )

    class Meta:
        model = SectionWiseExamResultStatus
        fields = [
            'id',
            'academic_year',
            'academic_year_name',
            'branch',
            'branch_name',
            'section',
            'section_name',
            'exam',
            'exam_name',
            'status_name',
            'finalized_at',
            'finalized_at_display',
            'finalized_by_username',
            'marks_completion_percentage',
            'marks_entry_expiry_datetime',
            'marks_entry_expiry_datetime_display',
            'is_progress_card_downloaded',
            'is_visible',
            'updated_at',
        ]
        read_only_fields = fields
