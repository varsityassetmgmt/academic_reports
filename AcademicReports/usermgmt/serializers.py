from django.contrib.auth.models import Permission, User, Group
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import *
import re

class PermissionSerializer_user_abilities(serializers.ModelSerializer):
    action = serializers.CharField(source='codename', read_only=True)
    subject = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = ('action', 'subject')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        # fields = ['name', 'id']
        fields = '__all__'

class CurrentUserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many = True)
    class Meta:
        model = get_user_model()
        fields = ("id", "username" ,"get_full_name", "email", "is_active", "is_staff", "is_superuser", 'groups')

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "is_active",
            "groups",
            "user_permissions",
        ]
        read_only_fields = ["id", "full_name", "is_active"]

    extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # Ensure password is not required
            'email': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def validate_email(self, value):
        """
        Ensure email is unique across users, ignore if blank.
        """
        if value and value.strip():  # Skip if email is empty or just whitespace
            user_model = get_user_model()
            user_qs = user_model.objects.filter(email__iexact=value.strip())
            if self.instance:
                user_qs = user_qs.exclude(pk=self.instance.pk)
            if user_qs.exists():
                raise serializers.ValidationError("This email is already in use.")
        return value


    def create(self, validated_data):
        groups_data = validated_data.pop('groups', None)
        user_permissions_data = validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            try:
                validate_password(password)
            except DjangoValidationError as e:
                raise serializers.ValidationError({'password': list(e.messages)})
            instance.set_password(password)  # Use set_password method to encrypt
        instance.save()
        if groups_data:
            instance.groups.set(groups_data)
        if user_permissions_data:
            instance.user_permissions.set(user_permissions_data)
        return instance

    def update(self, instance, validated_data):
        groups_data = validated_data.pop('groups', None)
        user_permissions_data = validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password is not None:
            try:
                validate_password(password)
            except DjangoValidationError as e:
                raise serializers.ValidationError({'password': list(e.messages)})
            instance.set_password(password)  # Use set_password method to encrypt

        instance.save()

        if groups_data is not None:
            instance.groups.set(groups_data)
        if user_permissions_data is not None:
            instance.user_permissions.set(user_permissions_data)
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username= serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id',
            'bio', 'phone_number',
            'states', 'zones', 'branches',
            'must_change_password', 'username',
            'academic_devisions',
        ]

    
    def validate_phone_number(self, value):
        if value and UserProfile.objects.filter(phone_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value
    
class AdminChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        # Check if passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Check for password length
        if len(new_password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', new_password):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', new_password):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        # Check for at least one number
        if not re.search(r'\d', new_password):
            raise serializers.ValidationError("Password must contain at least one number.")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class GroupsDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class PermssionsDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']