from rest_framework import serializers
from .models import *
from django.utils import timezone

# ==================== Subject ====================
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is')

    def validate_name(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Name is required.")
        qs = Subject.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A subject with this name already exists.")
        return value

    def validate_display_name(self, value):
        if value and len(value) > 250:
            raise serializers.ValidationError("Display name cannot exceed 250 characters.")
        return value

    def validate(self, attrs):
        academic_divisions = attrs.get('academic_devisions', [])
        class_names = attrs.get('class_names', [])
        if not academic_divisions and not class_names:
            raise serializers.ValidationError({
                "academic_devisions": "At least one academic division or class must be selected.",
                "class_names": "At least one academic division or class must be selected."
            })
        return attrs

# ==================== SubjectSkill ====================
class SubjectSkillSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SubjectSkill
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active')
    
    def validate_name(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Skill name is required.")
        
        # Check uniqueness per subject
        subject = self.initial_data.get('subject')
        qs = SubjectSkill.objects.filter(subject_id=subject, name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This skill already exists for the selected subject.")
        
        return value

    def validate(self, attrs):
        subject = attrs.get('subject') or getattr(self.instance, 'subject', None)
        if not subject:
            raise serializers.ValidationError({"subject": "Subject must be selected for this skill."})
        
        return attrs
 
# ==================== ExamType ====================
class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active')

    def validate_name(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Exam type name is required.")
        
        # Check uniqueness
        qs = ExamType.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("An exam type with this name already exists.")
        
        return value

# ==================== Exam ====================
class ExamSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    marks_entry_expiry_datetime_display = serializers.DateTimeField(source='marks_entry_expiry_datetime', format="%Y-%m-%d %H:%M:%S", read_only = True )

    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active', 'is_editable' ,'is_visible', 'is_progress_card_visible', 'exam_status')

    def validate_name(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Exam name is required.")
        
        academic_year = self.initial_data.get('academic_year')
        exam_type = self.initial_data.get('exam_type')
        qs = Exam.objects.filter(name__iexact=value, academic_year_id=academic_year, exam_type_id=exam_type)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("An exam with this name, year, and type already exists.")
        
        return value

    def validate(self, data):
        # Check editable
        if self.instance and self.instance.is_editable is False:
            raise serializers.ValidationError("This Exam is Already Published, Edit is not allowed.")

        # Check start and end date
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be earlier than start date."})

        # Ensure at least one selection for all ManyToMany fields
        m2m_fields = {
            "branches": data.get('branches', []),
            "states": data.get('states', []),
            "zones": data.get('zones', []),
            "orientations": data.get('orientations', []),
            "academic_devisions": data.get('academic_devisions', []),
            "student_classes": data.get('student_classes', []),
        }

        errors = {}
        for field_name, field_value in m2m_fields.items():
            if not field_value:
                errors[field_name] = f"At least one {field_name.replace('_', ' ')} must be selected."

        if errors:
            raise serializers.ValidationError(errors)
        
        marks_entry_expiry_datetime = data.get('marks_entry_expiry_datetime')
        if marks_entry_expiry_datetime and marks_entry_expiry_datetime <= timezone.localtime():
            raise serializers.ValidationError({
                "marks_entry_expiry_datetime": "Marks entry expiry datetime must be greater than the current time."
            })

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
        exam = data.get('exam') or getattr(self.instance, 'exam', None)
        subject = data.get('subject')
        exam_date = data.get('date')
        start_time = data.get('exam_start_time')
        end_time = data.get('exam_end_time')
        subject_skills = data.get('subject_skills', [])

        # Check if the related exam is editable
        if self.instance and self.instance.exam and not self.instance.exam.is_editable:
            raise serializers.ValidationError("This Exam is Already Published, Edit is not allowed.")

        # Validate exam date within range (inclusive)
        if exam and exam_date:
            if exam_date < exam.start_date or exam_date > exam.end_date:
                raise serializers.ValidationError({
                    "date": f"Exam instance date must be between {exam.start_date} and {exam.end_date}, inclusive."
                })

        # Validate exam start and end time
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({"exam_end_time": "Exam end time must be later than start time."})

        # Validate subject belongs to exam classes
        if exam and subject:
            exam_classes = exam.student_classes.all()
            subject_classes = subject.class_names.all()
            if exam_classes.exists() and subject_classes.exists():
                if not any(cls in subject_classes for cls in exam_classes):
                    raise serializers.ValidationError({
                        "subject": "Selected subject does not belong to any of the exam's classes."
                    })

        # Validate subject_skills belong to selected subject
        for skill in subject_skills:
            if skill.subject != subject:
                raise serializers.ValidationError({
                    "subject_skills": f"Skill '{skill.name}' does not belong to the selected subject '{subject.name}'."
                })

        # Validate at least one result type is selected
        if not (data.get('has_external_marks') or data.get('has_internal_marks') or data.get('has_subject_co_scholastic_grade')):
            raise serializers.ValidationError({
                "result_types": "At least one of external marks, internal marks, or co-scholastic grade must be selected."
            })

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

        # Validate skill belongs to the exam's subject
        if exam_instance and subject_skill:
            if subject_skill.subject != exam_instance.subject:
                raise serializers.ValidationError({
                    "subject_skill": "Selected skill does not belong to the exam's subject."
                })

        # Validate at least one result type is True
        if not (data.get('has_external_marks') or data.get('has_internal_marks') or data.get('has_subject_co_scholastic_grade')):
            raise serializers.ValidationError({
                "result_types": "At least one of external marks, internal marks, or co-scholastic grade must be selected."
            })

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

    def validate(self, data):
        marks_entry_expiry_datetime = data.get('marks_entry_expiry_datetime')

        # Validate marks_entry_expiry_datetime is in the future
        if marks_entry_expiry_datetime and marks_entry_expiry_datetime <= timezone.localtime():
            raise serializers.ValidationError({
                "marks_entry_expiry_datetime": "Marks entry expiry datetime must be greater than the current time."
            })

        return data

class SectionWiseExamResultStatusSerializer(serializers.ModelSerializer):
    # Readable names for related fields
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    class_name_display = serializers.CharField(source='section.class_name.name', read_only=True)
    orientation_name = serializers.CharField(source='section.orientation.name', read_only=True)
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
            'class_name_display',
            'orientation_name',
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

    def validate(self, data):
        marks_entry_expiry_datetime = data.get('marks_entry_expiry_datetime')

        # Validate marks_entry_expiry_datetime is in the future
        if marks_entry_expiry_datetime and marks_entry_expiry_datetime <= timezone.localtime():
            raise serializers.ValidationError({
                "marks_entry_expiry_datetime": "Marks entry expiry datetime must be greater than the current time."
            })

        # Optional: Ensure marks_completion_percentage is within 0-100
        percentage = data.get('marks_completion_percentage')
        if percentage is not None and (percentage < 0 or percentage > 100):
            raise serializers.ValidationError({
                "marks_completion_percentage": "Marks completion percentage must be between 0 and 100."
            })

        return data

