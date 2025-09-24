from rest_framework import serializers
from .models import ClassName, Orientation

# ==================== ClassName ====================
class ClassNameDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassName
        fields = ['id', 'name']  

# ==================== Orientation ====================
class OrientationDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orientation
        fields = ['id', 'name']  
