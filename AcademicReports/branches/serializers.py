from rest_framework import serializers
from .models import AcademicYear, AcademicDevision, State, Zone, Branch


# ==================== AcademicDevision ====================
class AcademicDevisionDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicDevision
        fields = ['id', 'name']


# ==================== State ====================
class StateDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']


# ==================== Zone ====================
class ZoneDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name']


# ==================== Branch ====================
class BranchDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']
