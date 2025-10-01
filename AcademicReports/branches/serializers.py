from rest_framework import serializers
from .models import AcademicYear, AcademicDevision, State, Zone, Branch


# ==================== AcademicDevision ====================
class AcademicDevisionDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicDevision
        fields = ['academic_devision_id', 'name']


# ==================== State ====================
class StateDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['state_id', 'name']


# ==================== Zone ====================
class ZoneDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['zone_id', 'name']


# ==================== Branch ====================
class BranchDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['branch_id', 'name']
