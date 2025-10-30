from rest_framework import serializers
from branches.models import *
from .models import *

# ==================== ClassName ====================
class ClassNameDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassName
        fields = ['class_name_id', 'name']  

# ==================== Orientation ====================
class OrientationDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orientation
        fields = ['orientation_id', 'name']  

class AdmissionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionStatus
        fields = ['admission_status_id', 'admission_status']


# ==================== Student Serializer ====================
class StudentSerializer(serializers.ModelSerializer):
    admission_status_name = serializers.CharField(source='admission_status.admission_status', read_only=True)
    state_name = serializers.CharField(source='branch.state.name', read_only=True)
    zone_name = serializers.CharField(source='branch.zone.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    orientation_name = serializers.CharField(source='orientation.name', read_only=True)
    student_class_name = serializers.CharField(source='student_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'academic_year',
            'SCS_Number',
            'name',
            'admission_status',
            'admission_status_name',
            'state_name',
            'zone_name',
            'branch',
            'branch_name',
            'orientation',
            'orientation_name',
            'student_class',
            'student_class_name',
            'section',
            'section_name',
            'is_active',
        ]
        read_only_fields = ('is_active',)

