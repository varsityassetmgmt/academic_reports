from rest_framework import serializers
from branches.models import *

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


# ==================== Student Serializer ====================
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
