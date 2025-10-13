from rest_framework import serializers
from .models import *
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import datetime

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
    exam_status_name = serializers.CharField(source='exam_status.name', read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active', 'is_editable' ,'is_visible', 'is_progress_card_visible', 'exam_status')

    def validate(self, data):
        # ---- 1. Prevent editing published exams ----
        if self.instance and self.instance.is_editable is False:
            raise serializers.ValidationError({"non_field_errors": "This Exam is already published, editing is not allowed."})

        # ---- 2. Duplicate name validation ----
        # fallback to instance values when updating
        name = self.initial_data.get('name') or getattr(self.instance, 'name', None)
        if not name or str(name).strip() == "":
            raise serializers.ValidationError({"name": "Exam name is required."})

        academic_year = (
            self.initial_data.get('academic_year')
            or (self.instance.academic_year_id if self.instance else None)
        )
        exam_type = (
            self.initial_data.get('exam_type')
            or (self.instance.exam_type_id if self.instance else None)
        )

        if academic_year and exam_type:
            qs = Exam.objects.filter(
                name__iexact=name.strip(),
                academic_year_id=academic_year,
                exam_type_id=exam_type
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "name": "An exam with this name, year, and type already exists."
                })

        # ---- 3. Date validation (start < end) ----
        start_date = data.get('start_date') or getattr(self.instance, 'start_date', None)
        end_date = data.get('end_date') or getattr(self.instance, 'end_date', None)

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be earlier than start date."})

        # ---- 4. Marks entry expiry datetime checks ----
        marks_entry_expiry_datetime = (
            data.get('marks_entry_expiry_datetime')
            or getattr(self.instance, 'marks_entry_expiry_datetime', None)
        )
        if not marks_entry_expiry_datetime:
            raise serializers.ValidationError({
                "marks_entry_expiry_datetime": "Marks entry expiry datetime must be selected."
            })

        now = timezone.now()
        if timezone.is_naive(marks_entry_expiry_datetime):
            marks_entry_expiry_datetime = timezone.make_aware(marks_entry_expiry_datetime)

        # 4a. Expiry must be in future
        if marks_entry_expiry_datetime <= now:
            raise serializers.ValidationError({
                "marks_entry_expiry_datetime": "Marks entry expiry datetime must be in the future."
            })

        # 4b. Expiry must be AFTER exam end date
        if end_date:
            end_of_day = timezone.make_aware(
                datetime.datetime.combine(end_date, datetime.time.max)
            )
            if marks_entry_expiry_datetime <= end_of_day:
                raise serializers.ValidationError({
                    "marks_entry_expiry_datetime": "Marks entry expiry datetime must be after the exam end date."
                })

        # ---- 5. M2M Field Validation ----
        # only validate during creation, not on update
        if not self.instance:
            m2m_fields = {
                "branches": self.initial_data.get('branches', []),
                "states": self.initial_data.get('states', []),
                "zones": self.initial_data.get('zones', []),
                "orientations": self.initial_data.get('orientations', []),
                "academic_devisions": self.initial_data.get('academic_devisions', []),
                "student_classes": self.initial_data.get('student_classes', []),
            }

            m2m_errors = {}
            for field_name, field_value in m2m_fields.items():
                if not field_value:
                    m2m_errors[field_name] = f"At least one {field_name.replace('_', ' ')} must be selected."

            if m2m_errors:
                raise serializers.ValidationError(m2m_errors)

        return data

    # def validate(self, data):
    #     # ---- 1. Prevent editing published exams ----
    #     if self.instance and self.instance.is_editable is False:
    #         raise serializers.ValidationError({"non_field_errors":"This Exam is Already Published, Edit is not allowed."})

    #     # ---- 2. Duplicate name validation ----
    #     name = self.initial_data.get('name')
    #     if not name or str(name).strip() == "":
    #         raise serializers.ValidationError({"name": "Exam name is required."})

    #     academic_year = self.initial_data.get('academic_year')
    #     exam_type = self.initial_data.get('exam_type')

    #     if academic_year and exam_type:
    #         qs = Exam.objects.filter(
    #             name__iexact=name.strip(),
    #             academic_year_id=academic_year,
    #             exam_type_id=exam_type
    #         )
    #         if self.instance:
    #             qs = qs.exclude(pk=self.instance.pk)
    #         if qs.exists():
    #             raise serializers.ValidationError({
    #                 "name": "An exam with this name, year, and type already exists."
    #             })

    #     # ---- 3. Date validation (start < end) ----
    #     start_date = data.get('start_date')
    #     end_date = data.get('end_date')
    #     if start_date and end_date and end_date < start_date:
    #         raise serializers.ValidationError({"end_date": "End date cannot be earlier than start date."})

    #     # ---- 4. Marks entry expiry datetime checks ----
    #     marks_entry_expiry_datetime = data.get('marks_entry_expiry_datetime')
    #     if not marks_entry_expiry_datetime:
    #         raise serializers.ValidationError({"endmarks_entry_expiry_datetime_date": " Marks entry expiry datetime must be selected.."})
    #     if marks_entry_expiry_datetime:
    #         from django.utils import timezone
    #         now = timezone.now()
    #         if timezone.is_naive(marks_entry_expiry_datetime):
    #             marks_entry_expiry_datetime = timezone.make_aware(marks_entry_expiry_datetime)

    #         # 4a. Expiry must be in future
    #         if marks_entry_expiry_datetime <= now:
    #             raise serializers.ValidationError({
    #                 "marks_entry_expiry_datetime": "Marks entry expiry datetime must be in the future."
    #             })

    #         # 4b. Expiry must be AFTER exam end date
    #         if end_date:
    #             # Convert end_date to datetime for proper comparison
    #             end_of_day = timezone.make_aware(
    #                 datetime.datetime.combine(end_date, datetime.time.max)
    #             )
    #             if marks_entry_expiry_datetime <= end_of_day:
    #                 raise serializers.ValidationError({
    #                     "marks_entry_expiry_datetime": "Marks entry expiry datetime must be after the exam end date."
    #                 })

    #     # ---- 5. Many-to-Many Field Validation ----
    #     m2m_fields = {
    #         "branches": self.initial_data.get('branches', []),
    #         "states": self.initial_data.get('states', []),
    #         "zones": self.initial_data.get('zones', []),
    #         "orientations": self.initial_data.get('orientations', []),
    #         "academic_devisions": self.initial_data.get('academic_devisions', []),
    #         "student_classes": self.initial_data.get('student_classes', []),
    #     }

    #     m2m_errors = {}
    #     for field_name, field_value in m2m_fields.items():
    #         if not field_value:
    #             m2m_errors[field_name] = f"At least one {field_name.replace('_', ' ')} must be selected."

    #     if m2m_errors:
    #         raise serializers.ValidationError(m2m_errors)

    #     return data

# ==================== ExamInstance ====================
class ExamInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_skill_names = serializers.SerializerMethodField()

    class Meta:
        model = ExamInstance
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'is_active')

    def get_subject_skill_names(self, obj):
        # Safely get related skill names if relation exists and not None
        if hasattr(obj, 'subject_skills') and obj.subject_skills.exists():
            return ', '.join(obj.subject_skills.values_list('name', flat=True))
        return ''
    
    def validate(self, data):
        exam = data.get('exam') or getattr(self.instance, 'exam', None)
        subject = data.get('subject')
        exam_date = data.get('date')
        start_time = data.get('exam_start_time')
        end_time = data.get('exam_end_time')
        subject_skills = data.get('subject_skills') or []

        # --- Prevent editing a published exam ---
        if self.instance and self.instance.exam and not self.instance.exam.is_editable:
            raise serializers.ValidationError({"non_field_errors":"This Exam is Already Published, Edit is not allowed."})

        # --- Validate exam date range ---
        if exam and exam_date:
            if not (exam.start_date <= exam_date <= exam.end_date):
                raise serializers.ValidationError({
                    "date": f"Exam date must be between {exam.start_date} and {exam.end_date}."
                })

        # --- Validate time logic ---
        if start_time and not end_time:
            raise serializers.ValidationError({"exam_end_time": "End time is required if start time is provided."})
        if end_time and not start_time:
            raise serializers.ValidationError({"exam_start_time": "Start time is required if end time is provided."})
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({"exam_end_time": "End time must be after start time."})

        # --- Validate subject belongs to exam's classes ---
        if exam and subject:
            exam_classes = exam.student_classes.all()
            subject_classes = subject.class_names.all()
            if exam_classes.exists() and subject_classes.exists():
                if not any(cls in subject_classes for cls in exam_classes):
                    raise serializers.ValidationError({
                        "subject": "Selected subject does not belong to any of the exam's classes."
                    })

        # --- Validate subject_skills belong to subject ---
        for skill in subject_skills:
            if skill.subject != subject:
                raise serializers.ValidationError({
                    "subject_skills": f"Skill '{skill.name}' does not belong to subject '{subject.name}'."
                })

        # --- Validate at least one result type selected ---
        has_external = data.get('has_external_marks')
        has_internal = data.get('has_internal_marks')
        has_skills = data.get('has_subject_skills')
        has_coscholastic = data.get('has_subject_co_scholastic_grade')

        if not (has_external or has_internal or has_coscholastic):
            raise serializers.ValidationError({
                "result_types": "At least one of external marks, internal marks, or co-scholastic grade must be selected."
            })

        # --- External marks validations ---
        if has_external:
            if not data.get('maximum_marks_external'):
                raise serializers.ValidationError({
                    "maximum_marks_external": "This field is required when external marks are enabled."
                })
            if not data.get('cut_off_marks_external'):
                raise serializers.ValidationError({
                    "cut_off_marks_external": "This field is required when external marks are enabled."
                })
            if (
                data.get('cut_off_marks_external') is not None
                and data.get('maximum_marks_external') is not None
                and data['cut_off_marks_external'] > data['maximum_marks_external']
            ):
                raise serializers.ValidationError({
                    "cut_off_marks_external": "Cut-off marks must be less than maximum marks for external."
                })

        # --- Internal marks validations ---
        if has_internal:
            if not data.get('maximum_marks_internal'):
                raise serializers.ValidationError({
                    "maximum_marks_internal": "This field is required when internal marks are enabled."
                })
            if not data.get('cut_off_marks_internal'):
                raise serializers.ValidationError({
                    "cut_off_marks_internal": "This field is required when internal marks are enabled."
                })
            if (
                data.get('cut_off_marks_internal') is not None
                and data.get('maximum_marks_internal') is not None
                and data['cut_off_marks_internal'] > data['maximum_marks_internal']
            ):
                raise serializers.ValidationError({
                    "cut_off_marks_internal": "Cut-off marks must be less than maximum marks for internal."
                })

        # --- Subject skills required if has_subject_skills=True ---
        if has_skills and not subject_skills:
            raise serializers.ValidationError({
                "subject_skills": "At least one subject skill must be selected when 'has_subject_skills' is enabled."
            })

        # --- Prevent duplicate instance for same exam, subject, and date ---
        existing = ExamInstance.objects.filter(exam=exam, subject=subject)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError({
                "non_field_errors": "An exam for this subject and date already exists."
            })

        return data


# ==================== Exam Skill Instance ====================
class ExamSubjectSkillInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='exam_instance.subject.name', read_only=True)
    subject_skill_name = serializers.CharField(source='subject_skill.name', read_only=True)

    class Meta:
        model = ExamSubjectSkillInstance
        fields = '__all__'
        read_only_fields = (
            'created_by',
            'updated_by',
            'is_active',
            'exam_instance',
            'subject_skill',
        )

    def validate(self, data):
        # exam_instance = data.get('exam_instance') or getattr(self.instance, 'exam_instance', None)
        # subject_skill = data.get('subject_skill') or getattr(self.instance, 'subject_skill', None)
        exam_instance = self.instance.exam_instance
        subject_skill = self.instance.subject_skill

        # ✅ 1. Ensure skill belongs to exam's subject
        if exam_instance and subject_skill and subject_skill.subject != exam_instance.subject:
            raise serializers.ValidationError({
                "subject_skill": "Selected skill does not belong to the exam's subject."
            })

        # ✅ 2. At least one result type
        has_external = data.get('has_external_marks', getattr(self.instance, 'has_external_marks', False))
        has_internal = data.get('has_internal_marks', getattr(self.instance, 'has_internal_marks', False))
        has_coscholastic = data.get('has_subject_co_scholastic_grade', getattr(self.instance, 'has_subject_co_scholastic_grade', False))

        if not (has_external or has_internal or has_coscholastic):
            raise serializers.ValidationError({
                "result_types": "At least one of external marks, internal marks, or co-scholastic grade must be selected."
            })

        # # ✅ 3. Marks validation
        # if has_external:
        #     max_external = data.get('maximum_marks_external', getattr(self.instance, 'maximum_marks_external', None))
        #     if max_external is None:
        #         raise serializers.ValidationError({
        #             "maximum_marks_external": "Required if external marks are enabled."
        #         })
        # if has_internal:
        #     max_internal = data.get('maximum_marks_internal', getattr(self.instance, 'maximum_marks_internal', None))
        #     if max_internal is None:
        #         raise serializers.ValidationError({
        #             "maximum_marks_internal": "Required if internal marks are enabled."
        #         })

        # --- External marks validations ---
        if has_external:
            if not data.get('maximum_marks_external'):
                raise serializers.ValidationError({
                    "maximum_marks_external": "This field is required when external marks are enabled."
                })
            if not data.get('cut_off_marks_external'):
                raise serializers.ValidationError({
                    "cut_off_marks_external": "This field is required when external marks are enabled."
                })
            if (
                data.get('cut_off_marks_external') is not None
                and data.get('maximum_marks_external') is not None
                and data['cut_off_marks_external'] > data['maximum_marks_external']
            ):
                raise serializers.ValidationError({
                    "cut_off_marks_external": "Cut-off marks must be less than maximum marks for external."
                })

        # --- Internal marks validations ---
        if has_internal:
            if not data.get('maximum_marks_internal'):
                raise serializers.ValidationError({
                    "maximum_marks_internal": "This field is required when internal marks are enabled."
                })
            if not data.get('cut_off_marks_internal'):
                raise serializers.ValidationError({
                    "cut_off_marks_internal": "This field is required when internal marks are enabled."
                })
            if (
                data.get('cut_off_marks_internal') is not None
                and data.get('maximum_marks_internal') is not None
                and data['cut_off_marks_internal'] > data['maximum_marks_internal']
            ):
                raise serializers.ValidationError({
                    "cut_off_marks_internal": "Cut-off marks must be less than maximum marks for internal."
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


class EditExamResultSerializer(serializers.ModelSerializer):
    external_marks = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    internal_marks = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ExamResult
        fields = [
            'exam_result_id',
            'student',
            'exam_instance',
            'exam_attendance',
            'external_marks',
            'internal_marks',
            'co_scholastic_grade',
        ]
        read_only_fields = [
            'exam_result_id',
            'student',
            'exam_instance',
        ]

    def validate(self, attrs):
        instance = self.instance
        exam_instance = instance.exam_instance
        marks_entry_expiry_datetime = exam_instance.exam.marks_entry_expiry_datetime
        exam = exam_instance.exam

        # ✅ 1. Marks entry lock validation
        if exam.exam_status_id == 3:  # assuming 3 = locked
            raise serializers.ValidationError({
                'exam': 'Exam marks entry is locked.'
            })

        if marks_entry_expiry_datetime and timezone.now() > marks_entry_expiry_datetime:
            raise serializers.ValidationError({
                'marks_entry_expiry_datetime': 'Marks Entry Time is Expired'
            })

        # ✅ If marks are not being updated, skip marks logic entirely
        if 'external_marks' not in attrs and 'internal_marks' not in attrs:
            return attrs

        # Default attendance = Present
        attendance_obj = None

        # Define valid absent/dropout keywords
        ABSENT_VALUES = ['AB', 'ABSENT', 'A', 'a']
        DROPOUT_VALUES = ['DR', 'DROPOUT', 'Drop', 'D', 'd']

        def parse_marks(value, field_name):
            """Parse and validate mark values."""
            if value in [None, ""]:
                return None  # empty input → None

            str_val = str(value).strip().upper()

            if str_val in ABSENT_VALUES:
                return "ABSENT"
            if str_val in DROPOUT_VALUES:
                return "DROPOUT"

            try:
                return Decimal(str(value))
            except (InvalidOperation, TypeError, ValueError):
                raise serializers.ValidationError({
                    field_name: f"Invalid input for {field_name}. Must be a number or 'AB' or 'DR'."
                })

        # ✅ Safely fetch values (only process ones included in the request)
        external_marks = attrs.get('external_marks', instance.external_marks)
        internal_marks = attrs.get('internal_marks', instance.internal_marks)

        ext_value = parse_marks(external_marks, "external_marks") if 'external_marks' in attrs else instance.external_marks
        int_value = parse_marks(internal_marks, "internal_marks") if 'internal_marks' in attrs else instance.internal_marks

        # Determine attendance
        if ext_value == "ABSENT" or int_value == "ABSENT":
            attrs['external_marks'] = None
            attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=2).first()  # Absent

        elif ext_value == "DROPOUT" or int_value == "DROPOUT":
            attrs['external_marks'] = None
            attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=3).first()  # Dropout

        else:
            # ✅ Range validation (only if those fields are being updated)
            if 'external_marks' in attrs and isinstance(ext_value, Decimal):
                if exam_instance.cut_off_marks_external is not None and ext_value > exam_instance.cut_off_marks_external:
                    raise serializers.ValidationError({
                        'external_marks': f'External Marks must be less than Cut off Marks ({exam_instance.cut_off_marks_external}) '
                    })

            if 'internal_marks' in attrs and isinstance(int_value, Decimal):
                if exam_instance.cut_off_marks_internal is not None and int_value > exam_instance.cut_off_marks_internal:
                    raise serializers.ValidationError({
                        'internal_marks': f'Internal Marks must be less than Cut off Marks ({exam_instance.cut_off_marks_internal}) '
                    })

            if 'external_marks' in attrs:
                attrs['external_marks'] = ext_value
            if 'internal_marks' in attrs:
                attrs['internal_marks'] = int_value
            try:
                attendance_obj = ExamAttendanceStatus.objects.get(exam_attendance_status_id=1)  # Present
            except ExamAttendanceStatus.DoesNotExist:
                pass

        if attendance_obj:
            attrs['exam_attendance'] = attendance_obj

        return attrs

class EditExamSkillResultSerializer(serializers.ModelSerializer):
    external_marks = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    internal_marks = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ExamSkillResult
        fields = [
            'exam_skill_result_id',
            'exam_result',
            'skill',
            'co_scholastic_grade',
            'exam_attendance',
            'external_marks',
            'internal_marks',
            'marks_obtained',
        ]
        read_only_fields = [
            'exam_skill_result_id',
            'exam_result',
            'skill',
            'marks_obtained',
        ]

    def validate(self, attrs):
        external_marks = attrs.get('external_marks')
        internal_marks = attrs.get('internal_marks')
        skill_result = self.instance

        # Fetch related ExamSubjectSkillInstance for cut-off info
        try:
            skill_instance = ExamSubjectSkillInstance.objects.get(
                exam_instance=skill_result.exam_result.exam_instance,
                subject_skill=skill_result.skill,
                is_active=True
            )
        except ExamSubjectSkillInstance.DoesNotExist:
            raise serializers.ValidationError(
                "ExamSubjectSkillInstance not found for this skill and exam."
            )

        exam = skill_instance.exam_instance.exam

        # ✅ 1. Marks entry lock validation
        if exam.exam_status_id == 3:  # assuming 3 = locked
            raise serializers.ValidationError({
                'exam': 'Exam marks entry is locked.'
            })

        
        marks_entry_expiry_datetime = skill_instance.exam_instance.exam.marks_entry_expiry_datetime
        if marks_entry_expiry_datetime and timezone.now() > marks_entry_expiry_datetime:
            raise serializers.ValidationError({'marks_entry_expiry_datetime': 'Marks Entry Time is Expired'})

        # Attendance handling
        attendance_obj = None
        ABSENT_VALUES = ['AB', 'ABSENT', 'A', 'a']
        DROPOUT_VALUES = ['DR', 'DROPOUT', 'Drop', 'D', 'd']

        def parse_marks(value, field_name, cut_off):
            if value in [None, ""]:
                return None

            str_val = str(value).strip().upper()

            # Handle Absent
            if str_val in ABSENT_VALUES:
                return "ABSENT"
            
            if str_val in DROPOUT_VALUES:
                return "DROPOUT"

            # Convert numeric
            try:
                dec_val = Decimal(value)
            except (TypeError, InvalidOperation):
                raise serializers.ValidationError(
                    {field_name: f"Invalid value for {field_name}. Must be numeric, 'AB', or 'DR'."}
                )

            if cut_off is not None and dec_val > cut_off:
                raise serializers.ValidationError(
                    {field_name: f"{field_name} cannot exceed cut-off ({cut_off})."}
                )
            return dec_val

        ext_value = parse_marks(external_marks, "external_marks", skill_instance.cut_off_marks_external)
        int_value = parse_marks(internal_marks, "internal_marks", skill_instance.cut_off_marks_internal)

        # Determine attendance
        if ext_value == "ABSENT" or int_value == "ABSENT":
            attrs['external_marks'] = None
            try:
                attendance_obj = ExamAttendanceStatus.objects.get(exam_attendance_status_id=2)  # Absent
            except ExamAttendanceStatus.DoesNotExist:
                pass
        elif ext_value == "DROPOUT" or int_value == "DROPOUT":
            attrs['external_marks'] = None
            try:
                attendance_obj = ExamAttendanceStatus.objects.get(exam_attendance_status_id=3)  # Dropout
            except ExamAttendanceStatus.DoesNotExist:
                pass
        else:
            # ✅ Range validation (only if those fields are being updated)
            if 'external_marks' in attrs and isinstance(ext_value, Decimal):
                if skill_instance.cut_off_marks_external is not None and ext_value > skill_instance.cut_off_marks_external:
                    raise serializers.ValidationError({
                        'external_marks': f'External Marks must be less than Cut off Marks ({skill_instance.cut_off_marks_external}) '
                    })

            if 'internal_marks' in attrs and isinstance(int_value, Decimal):
                if skill_instance.cut_off_marks_internal is not None and int_value > skill_instance.cut_off_marks_internal:
                    raise serializers.ValidationError({
                        'internal_marks': f'Internal Marks must be less than Cut off Marks ({skill_instance.cut_off_marks_internal}) '
                    })

            if 'external_marks' in attrs:
                attrs['external_marks'] = ext_value
            if 'internal_marks' in attrs:
                attrs['internal_marks'] = int_value
            try:
                attendance_obj = ExamAttendanceStatus.objects.get(exam_attendance_status_id=1)  # Present
            except ExamAttendanceStatus.DoesNotExist:
                pass

        # Set attendance if found
        if attendance_obj:
            attrs['exam_attendance'] = attendance_obj

        return attrs

class CoScholasticGradeDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoScholasticGrade
        fields =['id','name',]
