from rest_framework import serializers
from .models import ClassName, Orientation

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
