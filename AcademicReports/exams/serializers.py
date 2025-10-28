from rest_framework import serializers
from .models import *
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import datetime

# ==================== Subject Category ====================
class SubjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = ['id', 'name']

class SubjectCategoryDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = ['id', 'name']

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

        category = attrs.get('category') or getattr(self.instance, 'category', None)
        if not category:
            raise serializers.ValidationError({
                "category": "Category is required."
            })

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
    
# ==================== Exam Category ====================
class ExamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCategory
        fields = ['id', 'name']

class ExamCategoryDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCategory
        fields = ['id', 'name']

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
            raise serializers.ValidationError({"Exam": "This Exam is already published, editing is not allowed."})

        # ---- 2. Duplicate name validation ----
        # fallback to instance values when updating
        name = self.initial_data.get('name') or getattr(self.instance, 'name', None)
        if not name or str(name).strip() == "":
            raise serializers.ValidationError({"name": "Exam name is required."})
        
        category = self.initial_data.get('category') or getattr(self.instance, 'category', None)
        if not category:
            raise serializers.ValidationError({
                "category": "Category is required."
            })

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
    
    # def validate(self, data):
    #     exam = data.get('exam') or getattr(self.instance, 'exam', None)
    #     subject = data.get('subject')
    #     exam_date = data.get('date')
    #     start_time = data.get('exam_start_time')
    #     end_time = data.get('exam_end_time')
    #     subject_skills = data.get('subject_skills') or []

    #     # --- Prevent editing a published exam ---
    #     if self.instance and self.instance.exam and not self.instance.exam.is_editable:
    #         raise serializers.ValidationError({"non_field_errors":"This Exam is Already Published, Edit is not allowed."})

    #     # --- Validate exam date range ---
    #     if exam and exam_date:
    #         if not (exam.start_date <= exam_date <= exam.end_date):
    #             raise serializers.ValidationError({
    #                 "date": f"Exam date must be between {exam.start_date} and {exam.end_date}."
    #             })

    #     # --- Validate time logic ---
    #     if start_time and not end_time:
    #         raise serializers.ValidationError({"exam_end_time": "End time is required if start time is provided."})
    #     if end_time and not start_time:
    #         raise serializers.ValidationError({"exam_start_time": "Start time is required if end time is provided."})
    #     if start_time and end_time and end_time <= start_time:
    #         raise serializers.ValidationError({"exam_end_time": "End time must be after start time."})

    #     # --- Validate subject belongs to exam's classes ---
    #     if exam and subject:
    #         exam_classes = exam.student_classes.all()
    #         subject_classes = subject.class_names.all()
    #         if exam_classes.exists() and subject_classes.exists():
    #             if not any(cls in subject_classes for cls in exam_classes):
    #                 raise serializers.ValidationError({
    #                     "subject": "Selected subject does not belong to any of the exam's classes."
    #                 })

    #     # --- Validate subject_skills belong to subject ---
    #     for skill in subject_skills:
    #         if skill.subject != subject:
    #             raise serializers.ValidationError({
    #                 "subject_skills": f"Skill '{skill.name}' does not belong to subject '{subject.name}'."
    #             })

    #     # --- Validate at least one result type selected ---
    #     has_external = data.get('has_external_marks')
    #     has_internal = data.get('has_internal_marks')
    #     has_skills = data.get('has_subject_skills')
    #     has_coscholastic = data.get('has_subject_co_scholastic_grade')

    #     if not (has_external or has_internal or has_coscholastic):
    #         raise serializers.ValidationError({
    #             "result_types": "At least one of external marks, internal marks, or co-scholastic grade must be selected."
    #         })

    #     # --- External marks validations ---
    #     if has_external:
    #         if not data.get('maximum_marks_external'):
    #             raise serializers.ValidationError({
    #                 "maximum_marks_external": "This field is required when external marks are enabled."
    #             })
    #         if not data.get('cut_off_marks_external'):
    #             raise serializers.ValidationError({
    #                 "cut_off_marks_external": "This field is required when external marks are enabled."
    #             })
    #         if (
    #             data.get('cut_off_marks_external') is not None
    #             and data.get('maximum_marks_external') is not None
    #             and data['cut_off_marks_external'] > data['maximum_marks_external']
    #         ):
    #             raise serializers.ValidationError({
    #                 "cut_off_marks_external": "Cut-off marks must be less than maximum marks for external."
    #             })

    #     # --- Internal marks validations ---
    #     if has_internal:
    #         if not data.get('maximum_marks_internal'):
    #             raise serializers.ValidationError({
    #                 "maximum_marks_internal": "This field is required when internal marks are enabled."
    #             })
    #         if not data.get('cut_off_marks_internal'):
    #             raise serializers.ValidationError({
    #                 "cut_off_marks_internal": "This field is required when internal marks are enabled."
    #             })
    #         if (
    #             data.get('cut_off_marks_internal') is not None
    #             and data.get('maximum_marks_internal') is not None
    #             and data['cut_off_marks_internal'] > data['maximum_marks_internal']
    #         ):
    #             raise serializers.ValidationError({
    #                 "cut_off_marks_internal": "Cut-off marks must be less than maximum marks for internal."
    #             })

    #     # --- Subject skills required if has_subject_skills=True ---
    #     if has_skills and not subject_skills:
    #         raise serializers.ValidationError({
    #             "subject_skills": "At least one subject skill must be selected when 'has_subject_skills' is enabled."
    #         })

    #     # --- Prevent duplicate instance for same exam, subject, and date ---
    #     existing = ExamInstance.objects.filter(exam=exam, subject=subject)
    #     if self.instance:
    #         existing = existing.exclude(pk=self.instance.pk)
    #     if existing.exists():
    #         raise serializers.ValidationError({
    #             "non_field_errors": "An exam for this subject and date already exists."
    #         })

    #     return data


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
        exam = exam_instance.exam

        # ✅ Exam edit check
        if exam and not getattr(exam, "is_editable", True):
            raise serializers.ValidationError({f"Exam '{exam.name}' is locked. You cannot add or update exam instances for this exam."})

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

# ==================== CoScholasticGrade ====================
class CoScholasticGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoScholasticGrade
        fields = '__all__'
        read_only_fields = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')

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

class BranchWiseExamResultStatusSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam.exam_type.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    finalized_by_username = serializers.CharField(source='finalized_by.username', read_only=True)
    marks_entry_expiry_datetime_display = serializers.DateTimeField(source='marks_entry_expiry_datetime', format="%Y-%m-%d %H:%M:%S", read_only = True )
    finalized_at_display = serializers.DateTimeField(source='finalized_at', format="%Y-%m-%d %H:%M:%S", read_only = True )
    no_of_pending_vs_total_sections = serializers.SerializerMethodField()

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
            'exam_type_name',
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
            'no_of_pending_vs_total_sections',
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
            'no_of_pending_vs_total_sections',
        ]

    def get_no_of_pending_vs_total_sections(self, obj):
        pending = obj.number_of_sections_pending or 0
        total = obj.total_sections or 0
        return f'{pending}/{total}'

    def validate(self, data):
        marks_entry_expiry_datetime = data.get('marks_entry_expiry_datetime')
        end_date = self.instance.exam.end_date

        # Validate marks_entry_expiry_datetime is in the future
        if marks_entry_expiry_datetime and marks_entry_expiry_datetime <= timezone.localtime():
            raise serializers.ValidationError({
                "marks_entry_expiry_datetime": "Marks entry expiry datetime must be greater than the current time."
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
            'external_marks',
            'internal_marks',
            'co_scholastic_grade',
        ]
        read_only_fields = [
            'exam_result_id',
        ]

    def validate(self, attrs):
        instance = self.instance
        exam_instance = instance.exam_instance
        exam = exam_instance.exam

        # ✅ 1. Marks entry lock validation
        if exam.exam_status_id == 3:  # assuming 3 = locked
            raise serializers.ValidationError({'exam': 'Exam marks entry is locked.'})

        # ✅ 2. Marks entry expiry validation (branch-wise)
        branch = instance.student.branch
        branch_status = BranchWiseExamResultStatus.objects.filter(exam=exam, branch=branch).first()
        marks_entry_expiry_datetime = getattr(branch_status, 'marks_entry_expiry_datetime', None)

        if marks_entry_expiry_datetime and timezone.now() > marks_entry_expiry_datetime:
            raise serializers.ValidationError({'marks_entry_expiry_datetime': 'Marks entry time has expired.'})

        # ✅ If marks are not being updated, skip marks logic entirely
        updatable_fields = {'external_marks', 'internal_marks', 'co_scholastic_grade'}
        if not any(field in attrs for field in updatable_fields):
            return attrs

        attendance_obj = None

        # Valid text markers
        ABSENT_VALUES = ['AB']
        DROPOUT_VALUES = ['DR']
        INTERNAL_TRANSFER_VALUES = ['IT']

        # ---------- Helper functions ----------
        def parse_external_marks(value, field_name, cut_off):
            """Allow AB / DR / numeric for external marks"""
            if value in [None, ""]:
                return None

            str_val = str(value).strip().upper()
            if str_val in ABSENT_VALUES:
                return "ABSENT"
            if str_val in DROPOUT_VALUES:
                return "DROPOUT"
            if str_val in INTERNAL_TRANSFER_VALUES:
                return "INTERNAL_TRANSFER"

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

        def parse_internal_marks(value, field_name, cut_off):
            """Allow ONLY numeric or null/blank for internal marks"""
            if value in [None, ""]:
                return None

            str_val = str(value).strip()
            if str_val in ["", "."]:
                raise serializers.ValidationError(
                    {field_name: f"Invalid value for {field_name}. Only numeric values are allowed."}
                )
            if not str_val.replace('.', '', 1).isdigit():
                raise serializers.ValidationError(
                    {field_name: f"Invalid value for {field_name}. Only numeric values are allowed."}
                )

            try:
                dec_val = Decimal(value)
            except (TypeError, InvalidOperation):
                raise serializers.ValidationError(
                    {field_name: f"Invalid numeric value for {field_name}."}
                )

            if cut_off is not None and dec_val > cut_off:
                raise serializers.ValidationError(
                    {field_name: f"{field_name} cannot exceed cut-off ({cut_off})."}
                )
            return dec_val

        # ---------- Process external/internal marks ----------
        if 'external_marks' in attrs:
            external_marks = attrs.get('external_marks')
            ext_value = parse_external_marks(external_marks, "external_marks", exam_instance.cut_off_marks_external)

            # 🧠 Attendance logic → only when external marks are updated
            if ext_value == "ABSENT":
                attrs['external_marks'] = None
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=2).first()
            elif ext_value == "DROPOUT":
                attrs['external_marks'] = None
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=3).first()
            elif ext_value == 'INTERNAL_TRANSFER':
                attrs['external_marks'] = None
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=4).first()
            else:
                # Numeric external marks
                attrs['external_marks'] = ext_value
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=1).first()
        else:
            # ✅ No external marks update → keep current attendance
            ext_value = instance.external_marks

        if 'internal_marks' in attrs:
            internal_marks = attrs.get('internal_marks')
            int_value = parse_internal_marks(internal_marks, "internal_marks", exam_instance.cut_off_marks_internal)
            attrs['internal_marks'] = int_value

        # ✅ Update attendance only if external marks were sent
        if 'external_marks' in attrs and attendance_obj:
            attrs['exam_attendance'] = attendance_obj

        return attrs
    
    #  # ---------- Custom representation ----------
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     attendance = instance.exam_attendance
    #     is_present = attendance and attendance.exam_attendance_status_id == 1

    #     data['external_marks'] = (
    #         instance.external_marks if is_present
    #         else (attendance.short_code if attendance else None)
    #     )
        
    #     data['max_cut_off_marks_external'] = instance.cut_off_marks_external if instance else None

    #     return data

class EditExamSkillResultSerializer(serializers.ModelSerializer):
    external_marks = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    internal_marks = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ExamSkillResult
        fields = [
            'exam_skill_result_id',
            'co_scholastic_grade',
            'external_marks',
            'internal_marks',
        ]
        read_only_fields = [
            'exam_skill_result_id',
        ]

    def validate(self, attrs):
        instance = self.instance
        skill_result = instance

        # Get related ExamSubjectSkillInstance for cut-off info
        try:
            skill_instance = ExamSubjectSkillInstance.objects.get(
                exam_instance=skill_result.exam_result.exam_instance,
                subject_skill=skill_result.skill,
                is_active=True
            )
        except ExamSubjectSkillInstance.DoesNotExist:
            raise serializers.ValidationError(
                {"skill": "ExamSubjectSkillInstance not found for this skill and exam."}
            )

        exam = skill_instance.exam_instance.exam

        # ✅ 1. Marks entry lock validation
        if exam.exam_status_id == 3:  # assuming 3 = locked
            raise serializers.ValidationError({'exam': 'Exam marks entry is locked.'})


        # ✅ 2. Marks entry expiry validation (branch-wise)
        branch = skill_result.exam_result.student.branch
        branch_status = BranchWiseExamResultStatus.objects.filter(exam=exam, branch=branch).first()
        marks_entry_expiry_datetime = getattr(branch_status, 'marks_entry_expiry_datetime', None)

        if marks_entry_expiry_datetime and timezone.now() > marks_entry_expiry_datetime:
            raise serializers.ValidationError({
                'marks_entry_expiry_datetime': 'Marks entry time has expired.'
            })

        # ✅ If marks are not being updated, skip marks logic entirely
        updatable_fields = {'external_marks', 'internal_marks', 'co_scholastic_grade'}
        if not any(field in attrs for field in updatable_fields):
            return attrs

        attendance_obj = None
        ABSENT_VALUES = ['AB']
        DROPOUT_VALUES = ['DR']
        INTERNAL_TRANSFER_VALUES = ['IT']

        # --- Helper functions ---
        def parse_external_marks(value, field_name, cut_off):
            """Allow AB / DR / numeric for external marks"""
            if value in [None, ""]:
                return None

            str_val = str(value).strip().upper()
            if str_val in ABSENT_VALUES:
                return "ABSENT"
            if str_val in DROPOUT_VALUES:
                return "DROPOUT"
            if str_val in INTERNAL_TRANSFER_VALUES:
                return "INTERNAL_TRANSFER"

            try:
                dec_val = Decimal(value)
            except (TypeError, InvalidOperation):
                raise serializers.ValidationError({
                    field_name: f"Invalid value for {field_name}. Must be numeric, 'AB', or 'DR'."
                })

            if cut_off is not None and dec_val > cut_off:
                raise serializers.ValidationError({
                    field_name: f"{field_name} cannot exceed cut-off ({cut_off})."
                })
            return dec_val

        # ---------- Helper functions ----------
        def parse_external_marks(value, field_name, cut_off):
            """Allow AB / DR / numeric for external marks"""
            if value in [None, ""]:
                return None

            str_val = str(value).strip().upper()
            if str_val in ABSENT_VALUES:
                return "ABSENT"
            if str_val in DROPOUT_VALUES:
                return "DROPOUT"
            if str_val in INTERNAL_TRANSFER_VALUES:
                return "INTERNAL_TRANSFER"

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

        def parse_internal_marks(value, field_name, cut_off):
            """Allow ONLY numeric or null/blank for internal marks"""
            if value in [None, ""]:
                return None

            str_val = str(value).strip()
            if str_val in ["", "."]:
                raise serializers.ValidationError(
                    {field_name: f"Invalid value for {field_name}. Only numeric values are allowed."}
                )
            if not str_val.replace('.', '', 1).isdigit():
                raise serializers.ValidationError(
                    {field_name: f"Invalid value for {field_name}. Only numeric values are allowed."}
                )

            try:
                dec_val = Decimal(value)
            except (TypeError, InvalidOperation):
                raise serializers.ValidationError(
                    {field_name: f"Invalid numeric value for {field_name}."}
                )

            if cut_off is not None and dec_val > cut_off:
                raise serializers.ValidationError(
                    {field_name: f"{field_name} cannot exceed cut-off ({cut_off})."}
                )
            return dec_val
        
        if 'external_marks' in attrs:
            external_marks = attrs.get('external_marks')
            ext_value = parse_external_marks(external_marks, "external_marks", skill_instance.cut_off_marks_external)

            # 🧠 Attendance logic → only when external marks are updated
            if ext_value == "ABSENT":
                attrs['external_marks'] = None
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=2).first()
            elif ext_value == "DROPOUT":
                attrs['external_marks'] = None
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=3).first()
            elif ext_value == 'INTERNAL_TRANSFER':
                attrs['external_marks'] = None
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=4).first()
            else:
                # Numeric external marks
                attrs['external_marks'] = ext_value
                attendance_obj = ExamAttendanceStatus.objects.filter(exam_attendance_status_id=1).first()
        else:
            # ✅ No external marks update → keep current attendance
            ext_value = instance.external_marks

        if 'internal_marks' in attrs:
            internal_marks = attrs.get('internal_marks')
            int_value = parse_internal_marks(internal_marks, "internal_marks", skill_instance.cut_off_marks_internal)
            attrs['internal_marks'] = int_value

        # ✅ Update attendance only if external marks were sent
        if 'external_marks' in attrs and attendance_obj:
            attrs['exam_attendance'] = attendance_obj

        return attrs

    # # ==================== CUSTOM REPRESENTATION ====================
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     attendance = instance.exam_attendance
    #     is_present = attendance and attendance.exam_attendance_status_id == 1

    #     data['external_marks'] = (
    #         instance.external_marks if is_present
    #         else (attendance.short_code if attendance else None)
    #     )
        
    #     data['max_cut_off_marks_external'] = instance.cut_off_marks_external if instance else None

    #     return data

class CoScholasticGradeDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoScholasticGrade
        fields =['id','name',]



#===============================================================  Create Exam Instance  =========================================================================

# # serializers.py
# from rest_framework import serializers
# from .models import ExamInstance, SubjectSkill

# class CreateExamInstanceSerializer(serializers.ModelSerializer):
#     # Use PK related fields so API accepts integer IDs
#     exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all())
#     subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
#     subject_skills = serializers.PrimaryKeyRelatedField(queryset=SubjectSkill.objects.all(), many=True, required=False)

#     class Meta:
#         model = ExamInstance
#         fields = '__all__'

#     def validate(self, attrs):
#         exam = attrs.get('exam') or (self.instance.exam if self.instance else None)
#         subject = attrs.get('subject') or (self.instance.subject if self.instance else None)
#         date = attrs.get('date') or (self.instance.date if self.instance else None)
#         start = attrs.get('exam_start_time') or (self.instance.exam_start_time if self.instance else None)
#         end = attrs.get('exam_end_time') or (self.instance.exam_end_time if self.instance else None)
#         subject_skills = attrs.get('subject_skills', [])
#         has_co_scholastic = attrs.get('has_subject_co_scholastic_grade', False)

#         has_external = attrs.get('has_external_marks', False)
#         max_external = attrs.get('maximum_marks_external')
#         cut_off_external = attrs.get('cut_off_marks_external')
#         has_internal = attrs.get('has_internal_marks', False)
#         max_internal = attrs.get('maximum_marks_internal')
#         cut_off_internal = attrs.get('cut_off_marks_internal')

#         # Validate co-scholastic grade + subject_skills
#         if has_co_scholastic and not subject_skills:
#             raise serializers.ValidationError({
#                 "subject_skills": "At least one subject skill is required when co-scholastic grade is enabled."
#             })
        
#         # exam edit check
#         if exam and not getattr(exam, "is_editable", True):
#             raise serializers.ValidationError({"exam": f"'{exam.name}' is locked. Cannot add or update ExamInstances."})
        
#         # required exam+subject
#         if not exam or not subject:
#             raise serializers.ValidationError("Exam and Subject are required.")

#         # date within exam
#         if date and (not (exam.start_date <= date <= exam.end_date)):
#             raise serializers.ValidationError({"date": f"Exam date must be between {exam.start_date} and {exam.end_date}."})

#         # time check
#         if start and end and start >= end:
#             raise serializers.ValidationError({"exam_end_time": "Exam end time must be later than start time."})

#         # unique check: on create exclude nothing, on update exclude instance
#         qs = ExamInstance.objects.filter(exam=exam, subject=subject)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise serializers.ValidationError("An ExamInstance with this Exam and Subject already exists.")
        
#         # External marks validation
#         if has_external:
#             if max_external is None:
#                 raise serializers.ValidationError("This max external marks is required when external marks are enabled.")
#             if cut_off_external is None:
#                 raise serializers.ValidationError("This cut off external is required when external marks are enabled.")
#             elif max_external is not None and cut_off_external > max_external:
#                 raise serializers.ValidationError("Cut-off external marks cannot be greater than maximum external marks.")
            
#         # Internal marks validation
#         if has_internal:
#             if max_internal is None:
#                 raise serializers.ValidationError("Maximum internal marks  required when internal marks are enabled.")
                
#             if cut_off_internal is None:
#                 raise serializers.ValidationError("cut off insternal marks  is required when internal marks are enabled.")
#             elif max_internal is not None and cut_off_internal > max_internal:
#                 raise serializers.ValidationError("Cut-off internal marks cannot be greater than maximum internal marks.")
    
#         return attrs

#     def create(self, validated_data):
#         subject_skills = validated_data.pop('subject_skills', [])
#         instance = super().create(validated_data)
#         if subject_skills:
#             instance.subject_skills.set(subject_skills)
#         return instance

#     def update(self, instance, validated_data):
#         subject_skills = validated_data.pop('subject_skills', None)
#         instance = super().update(instance, validated_data)
#         if subject_skills is not None:
#             instance.subject_skills.set(subject_skills)
#         return instance



# serializers.py
from rest_framework import serializers
from .models import ExamInstance, SubjectSkill, Exam, Subject


class CreateExamInstanceSerializer(serializers.ModelSerializer):
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    subject_skills = serializers.PrimaryKeyRelatedField(
        queryset=SubjectSkill.objects.all(), many=True, required=False
    )
    read_only_fields = ('created_by', 'updated_by', 'is_active')

    class Meta:
        model = ExamInstance
        fields = '__all__'

    def validate(self, attrs):
        exam = attrs.get('exam') or (self.instance.exam if self.instance else None)
        subject = attrs.get('subject') or (self.instance.subject if self.instance else None)
        date = attrs.get('date') or (self.instance.date if self.instance else None)
        start = attrs.get('exam_start_time') or (self.instance.exam_start_time if self.instance else None)
        end = attrs.get('exam_end_time') or (self.instance.exam_end_time if self.instance else None)
        subject_skills = attrs.get('subject_skills', [])
        has_subject_skills = attrs.get('has_subject_skills', getattr(self.instance, 'has_subject_skills', False))

        has_external = attrs.get('has_external_marks', getattr(self.instance, 'has_external_marks', False))
        max_external = attrs.get('maximum_marks_external')
        cut_off_external = attrs.get('cut_off_marks_external')

        has_internal = attrs.get('has_internal_marks', getattr(self.instance, 'has_internal_marks', False))
        max_internal = attrs.get('maximum_marks_internal')
        cut_off_internal = attrs.get('cut_off_marks_internal')

        has_coscholastic = attrs.get('has_subject_co_scholastic_grade', getattr(self.instance, 'has_subject_co_scholastic_grade', False))

        errors = {}

        # ✅ Co-scholastic grade + subject_skills validation
        if has_subject_skills and not subject_skills:
            errors["subject_skills"] = "At least one subject skill must be selected when Has Subject Skill is enabled."

        # ✅ Exam edit check
        if exam and not getattr(exam, "is_editable", True):
            errors["exam"] = f"Exam '{exam.name}' is locked. You cannot add or update exam instances for this exam."

        # ✅ Required exam and subject check
        if not exam:
            errors["exam"] = "Exam selection is required."
        if not subject:
            errors["subject"] = "Subject selection is required."

        # ✅ Date within exam range
        if exam and date:
            if not (exam.start_date <= date <= exam.end_date):
                errors["date"] = f"The exam date ({date}) must be between {exam.start_date} and {exam.end_date}."

        # ✅ Start < End time
        if start and end and start >= end:
            errors["exam_end_time"] = "Exam end time must be later than the start time."

        # ✅ Unique exam + subject constraint
        qs = ExamInstance.objects.filter(exam=exam, subject=subject)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            errors["subject"] = "An exam instance already exists for this subject in the selected exam."

        # ✅ External marks validation
        if has_external:
            if max_external is None:
                errors["maximum_marks_external"] = "Maximum external marks are required when external marks are enabled."
            if cut_off_external is None:
                errors["cut_off_marks_external"] = "Cut-off external marks are required when external marks are enabled."
            elif max_external is not None and cut_off_external > max_external:
                errors["cut_off_marks_external"] = "Cut-off external marks cannot exceed the maximum external marks."

        # ✅ Internal marks validation
        if has_internal:
            if max_internal is None:
                errors["maximum_marks_internal"] = "Maximum internal marks are required when internal marks are enabled."
            if cut_off_internal is None:
                errors["cut_off_marks_internal"] = "Cut-off internal marks are required when internal marks are enabled."
            elif max_internal is not None and cut_off_internal > max_internal:
                errors["cut_off_marks_internal"] = "Cut-off internal marks cannot exceed the maximum internal marks."

        # ✅ At least one result type must be enabled
        if not (has_external or has_internal or has_coscholastic or has_subject_skills):
            errors["result_types"] = (
                "At least one of external marks, internal marks, co-scholastic grade, or subject skills must be selected."
            )

        category = self.initial_data.get('sequence') or getattr(self.instance, 'sequence', None)
        if not category:
            raise serializers.ValidationError({
                "Sequence": "Sequence is required."
            })

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        subject_skills = validated_data.pop('subject_skills', [])
        instance = super().create(validated_data)
        if subject_skills:
            instance.subject_skills.set(subject_skills)
        return instance

    def update(self, instance, validated_data):
        subject_skills = validated_data.pop('subject_skills', None)
        instance = super().update(instance, validated_data)
        if subject_skills is not None:
            instance.subject_skills.set(subject_skills)
        return instance


class ExamStatusDropDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamStatus
        fields = ['id', 'name']

class ExamResultStatusDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResultStatus
        fields = ['id', 'name']

class ViewExamSubjectSkillInstanceSerializer(serializers.ModelSerializer):
    subject_skill_name = serializers.CharField(source='subject_skill.name', read_only=True)

    class Meta:
        model = ExamSubjectSkillInstance
        fields = [
            'subject_skill_name',
            'has_external_marks',
            'maximum_marks_external',
            'cut_off_marks_external',
            'has_internal_marks',
            'maximum_marks_internal',
            'cut_off_marks_internal',
            'has_subject_co_scholastic_grade',
        ]


class ViewExamInstanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    date = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    subject_skills = serializers.SerializerMethodField()

    class Meta:
        model = ExamInstance
        fields = [
            'subject_name',
            'date',
            'start_time',
            'end_time',
            'is_optional',
            'has_external_marks',
            'maximum_marks_external',
            'cut_off_marks_external',
            'has_internal_marks',
            'maximum_marks_internal',
            'cut_off_marks_internal',
            'has_subject_co_scholastic_grade',
            'has_subject_skills',
            'subject_skills',
        ]

    def get_date(self, obj):
        return obj.date.strftime("%d-%b-%Y") if obj.date else None

    def get_start_time(self, obj):
        return obj.exam_start_time.strftime("%I:%M %p") if obj.exam_start_time else None

    def get_end_time(self, obj):
        return obj.exam_end_time.strftime("%I:%M %p") if obj.exam_end_time else None

    def get_subject_skills(self, obj):
        skills_qs = obj.exam_subject_skills_instance_exam_instance.filter(is_active=True)
        return ViewExamSubjectSkillInstanceSerializer(skills_qs, many=True).data


class ViewExamSerializer(serializers.ModelSerializer):
    exam_type = serializers.CharField(source='exam_type.name', default=None)
    academic_year = serializers.CharField(source='academic_year.name', default=None)
    exam_status = serializers.CharField(source='exam_status.name', default=None)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    marks_entry_expiry_datetime = serializers.SerializerMethodField()
    marks_entry_expiry_datetime_backup = serializers.SerializerMethodField()
    Subjects = ViewExamInstanceSerializer(source='exam_instance_exam', many=True)

    class Meta:
        model = Exam
        fields = [
            'exam_type',
            'name',
            'academic_year',
            'exam_status',
            'start_date',
            'end_date',
            'marks_entry_expiry_datetime',
            'marks_entry_expiry_datetime_backup',
            'is_visible',
            'is_progress_card_visible',
            'Subjects'
        ]

    def get_start_date(self, obj):
        return obj.start_date.strftime("%d-%b-%Y") if obj.start_date else None

    def get_end_date(self, obj):
        return obj.end_date.strftime("%d-%b-%Y") if obj.end_date else None

    def get_marks_entry_expiry_datetime(self, obj):
        if obj.marks_entry_expiry_datetime:
            return timezone.localtime(obj.marks_entry_expiry_datetime).strftime("%d-%b-%Y %I:%M %p")
        return None

    def get_marks_entry_expiry_datetime_backup(self, obj):
        if obj.marks_entry_expiry_datetime:
            return timezone.localtime(obj.marks_entry_expiry_datetime).strftime("%Y-%m-%d %H:%M:%S")
        return None
