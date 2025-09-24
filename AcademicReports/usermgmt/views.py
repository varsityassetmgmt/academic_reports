from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import *
from .serializers import *
from .models import *
from usermgmt.custompagination import CustomPagination
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.signals import user_logged_in
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from django.contrib.auth import update_session_auth_hash
from branches.serializers import AcademicDevisionDropdownSerializer, StateDropdownSerializer, ZoneDropdownSerializer, BranchDropdownSerializer


#========================================= Login Views ===========================================
class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        login_input = attrs.get('username')
        password = attrs.get('password')

        if not login_input:
            raise serializers.ValidationError({"username": "This field is required."})

        # 1. Try finding user by username or email
        user = get_user_model().objects.filter(
            Q(username=login_input) | Q(email=login_input)
        ).first()

        if not user:
            try:
                user_profile = UserProfile.objects.get(phone_number=login_input)
                user = user_profile.user
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError({"username": "Invalid login id / email / phone number."})

        user = authenticate(
            request=self.context.get('request'),
            username=user.username,  # Use username here even if logged in via email
            password=password
        )

        if user is None:
            raise serializers.ValidationError({"password": "Password is incorrect."})

        # Send login signal
        user_logged_in.send(sender=user.__class__, request=self.context.get("request"), user=user)

        # Generate token
        refresh = RefreshToken.for_user(user)
        refresh["custom_field"] = "Custom value"

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        # Add user data
        user_serializer = CurrentUserSerializer(user)
        data['userData'] = user_serializer.data

        # Add user profile
        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile:
            data['userProfileData'] = UserProfileSerializer(user_profile).data
            data["is_firstlogin"] = user_profile.must_change_password
        else:
            data['userProfileData'] = None
            data["is_firstlogin"] = False

        # Add permissions
        permissions_user_abilities = Permission.objects.filter(
            Q(user=user) | Q(group__user=user)
        ).distinct()
        permission_serializer = PermissionSerializer_user_abilities(permissions_user_abilities, many=True)
        data["userAbilities"] = permission_serializer.data

        return data
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#================================= User ViewSet =============================================
class UserViewset(ModelViewSet):
    permission_classes = (CanViewUser, CanAddUser, CanChangeUser)
    serializer_class = UserSerializer
    # queryset = get_user_model().objects.filter(is_active=True).order_by('-id')
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    search_fields = ['id', 'email', 'username', 'first_name', 'last_name']
    ordering_fields = ['id', 'email', 'username', 'first_name', 'last_name']
    filterset_fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active']
    http_method_names = ['get', 'post', 'put', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(id=1).exists():
            return get_user_model().objects.filter(is_active=True).order_by('-id')
        else:
            return get_user_model().objects.filter(Q(is_active=True) & Q(id = user.id)).order_by('-id')
        
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewUser]
        elif self.action == 'create':
            permission_classes = [CanAddUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanChangeUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            return Response({'errors': exc.detail}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValidationError as exc:
            return Response({'errors': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        
#=================================== User Profile =========================================
class UserProfileViewSet(ModelViewSet):
    serializer_class = UserProfileSerializer
    # queryset = UserProfile.objects.all().order_by("-id")
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]  # Added DjangoFilterBackend for filtering
    search_fields = [
        'user__username', 
        'user__email',  # Added Email for searching
        'user__first_name',  # Added First Name for searching
        'user__last_name',  # Added Last Name for searching
    ]
    filterset_fields = [
        'user__username', 
        'user__email',  # Added Email for filtering
        'user__first_name',  # Added First Name for filtering
        'user__last_name',  # Added Last Name for filtering
    ]
    http_method_names = ['get', 'put', 'head', 'options']  # ,'post'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(id=1).exists():
            users = get_user_model().objects.filter(is_active=True).values_list('id', flat=True).order_by('-id')
            return UserProfile.objects.filter(user_id__in=users)
        else:
            return UserProfile.objects.filter(user=user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Assuming 'list' is the view action
            permission_classes = [CanViewUserProfile]
        elif self.action == 'create':  # Assuming 'create' is the add action
            permission_classes = [CanAddUserProfile]
        elif self.action in ['update', 'partial_update']:  # Assuming these are change actions
            permission_classes = [CanChangeUserProfile]
        else:
            permission_classes = [permissions.AllowAny]  # Default to allow any
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'message': 'User Profile created successfully'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'message': 'User Profile updated successfully'}, status=status.HTTP_200_OK)
    
#=====================================================  Change password first loging ==================================================================================

@api_view(['POST']) #,'PUT'
@permission_classes([IsAuthenticated])
def change_password_first_login(request):
    user = request.user
    new_password = request.data.get("new_password", "")
    confirm_password = request.data.get("confirm_password", "")
    
    if new_password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    user.set_password(new_password)
    user.save()

    # Update session to keep the user logged in after password change
    update_session_auth_hash(request, user)

    user_profile = UserProfile.objects.get(user_id  = user.id)
    user_profile.must_change_password = False
    user_profile.save()

    return Response({"success": "Password changed successfully"}, status=status.HTTP_200_OK)

#============================================================ Password Chage By User ===============================================================================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_by_user(request):
    user = request.user
    old_password = request.data.get("old_password", "")
    new_password = request.data.get("new_password", "")
    confirm_password = request.data.get("confirm_password", "")

    # Check if the old password is correct
    if not user.check_password(old_password):
        return Response({"old_password": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the new password is the same as the current password (using check_password)
    if user.check_password(new_password):
        return Response({"new_password": "New password must not be the same as the current password"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the new password and confirm password match
    if new_password != confirm_password:
        return Response({"confirm_password": "New passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the new password (using Django's validators)
    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    user.set_password(new_password)
    user.save()

    # Update session to keep the user logged in after password change
    update_session_auth_hash(request, user)

    # Disable `must_change_password` flag if it exists

    return Response({"success": "Password changed successfully"}, status=status.HTTP_200_OK)

#============================================================ Password Chage By Admin ===============================================================================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated,CanChangePassword])
def user_change_password_by_admin(request, user_id=None):
    if request.method == "PUT":
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminChangePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            context = {
                'message': "Password updated successfully."
            }
            return Response(context, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Invalid request method."}, status=status.HTTP_400_BAD_REQUEST)

#================================================================================Group ViewSet =======================================================================================================================
class GroupViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated)
    serializer_class = GroupSerializer
    queryset = Group.objects.all().order_by('-id')
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'id']
    ordering_fields = ['name', 'id']
    filterset_fields = ['name', 'id']
    http_method_names = ['get', 'post', 'put', 'head', 'options']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Assuming 'list' is the view action
            permission_classes = [CanViewGroup]
        elif self.action == 'create':  # Assuming 'create' is the add action
            permission_classes = [CanAddGroup]
        elif self.action in ['update', 'partial_update']:  # Assuming these are change actions
            permission_classes = [CanChangeGroup]
        else:
            permission_classes = [permissions.AllowAny] 
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'message': 'User Group created successfully'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'message': 'User Group updated successfully'}, status=status.HTTP_200_OK)
    
# =============================== Groups dropdown ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_groups_dropdown(request):
    groups = Group.objects.all().order_by('name')
    if groups:
        serializer = GroupsDropDownSerializer(groups, many=True)
        context = {
            'message': "data successfully obtained",
            'results': serializer.data
        }
        return Response(context, status=status.HTTP_200_OK)

    else:
        context = {
            'message': "Data not found",
            'results': []
        }
        return Response(context,status=status.HTTP_200_OK)

# ================================ permissions  dropdown for Group ============================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_permissions_dropdown(request):
    unwanted_permssions_id_list = []
    delete_permissions = Permission.objects.filter(codename__contains="delete").values_list('id', flat=True)

    delete_permissions_list = list(delete_permissions)
    resultList= list(set(unwanted_permssions_id_list) | set(delete_permissions_list))
    try:
        permissions = Permission.objects.all().exclude(id__in = resultList).order_by('content_type__model')
    except:
        permissions = Permission.objects.all().exclude(id__in = delete_permissions_list).order_by('content_type__model')
    if permissions:
        serializer = PermssionsDropdownSerializer(permissions, many=True)
        context = {
            'message': "data successfully obtained",
            'results': serializer.data
        }
        return Response(context, status=status.HTTP_200_OK)

    else:
        context = {
            'message': "Data not found",
            'results': []
        }
        return Response(context, status=status.HTTP_200_OK)
    
#============================================ Permissions Dropdown Exclude Groups (for users extra permissions) =======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_permissions_dropdown_exclude_groups(request,group_list=None):
    if not (group_list ==None):
        group_list = group_list
        group_list = group_list.split(",")
        group_permissions      = Permission.objects.filter(group__in = group_list).distinct().values_list('id', flat=True)
        group_permissions_list = list(group_permissions)
    else:
        group_permissions_list = []

    unwanted_permssions_id_list = []
    delete_permissions = Permission.objects.filter(codename__contains="delete").values_list('id', flat=True)
    delete_permissions_list = list(delete_permissions)

    resultList= list(set(unwanted_permssions_id_list) | set(delete_permissions_list))

    final_list  = list(set(resultList) | set(group_permissions_list))

    resultList2 =   list(set(delete_permissions_list) | set(group_permissions_list))

    try:
        permissions = Permission.objects.all().exclude(id__in = final_list).order_by('content_type__model')
    except:
        permissions = Permission.objects.all().exclude(id__in = resultList2).order_by('content_type__model')
    if permissions:
        serializer = PermssionsDropdownSerializer(permissions, many=True)
        context = {
            'message': "data successfully obtained",
            'results': serializer.data
        }
        return Response(context, status=status.HTTP_200_OK)

    else:
        context = {
            'message': "Data not found",
            'results': []
        }
        return Response(context, status=status.HTTP_200_OK) 
    
#=============================== Academic Devision,  State, Zone, Branch Dropdowns for UserProfile
class AcademicDevisionDropdownForUserProfileViewSet(ModelViewSet):
    queryset = AcademicDevision.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = AcademicDevisionDropdownSerializer
    http_method_names = ['GET',]

class StateDropdownForUserProfileViewSet(ModelViewSet):
    queryset = State.objects.filter(is_active=True).order_by('name')
    permission_classes = [IsAuthenticated]
    serializer_class = StateDropdownSerializer
    http_method_names = ['GET',]

class ZoneDropdownForUserProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ZoneDropdownSerializer
    http_method_names = ['GET',]

    def get_queryset(self):
        # Get 'state_ids' query parameter (comma-separated)
        state_ids_str = self.request.GET.get('state_ids', '')  # e.g., "1,2,3" or empty
        queryset = Zone.objects.filter(is_active=True).order_by('name')

        if state_ids_str.strip():  # Only exclude if non-empty
            try:
                state_ids = [int(sid) for sid in state_ids_str.split(',') if sid.isdigit()]
                if state_ids:
                    queryset = queryset.exclude(state_id__in=state_ids)
            except ValueError:
                pass  # Ignore invalid input

        return queryset

class BranchDropdownForUserProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BranchDropdownSerializer

    def get_queryset(self):
        # Get query params
        state_ids_str = self.request.GET.get('state_ids', '')  # e.g., "1,2,3"
        zone_ids_str = self.request.GET.get('zone_ids', '')    # e.g., "5,7"

        queryset = Branch.objects.filter(is_active=True).order_by('name')

        # Exclude branches based on state_ids
        if state_ids_str.strip():
            try:
                state_ids = [int(sid) for sid in state_ids_str.split(',') if sid.isdigit()]
                if state_ids:
                    queryset = queryset.exclude(state_id__in=state_ids)
            except ValueError:
                pass  # Ignore invalid input

        # Exclude branches based on zone_ids
        if zone_ids_str.strip():
            try:
                zone_ids = [int(zid) for zid in zone_ids_str.split(',') if zid.isdigit()]
                if zone_ids:
                    queryset = queryset.exclude(zone_id__in=zone_ids)
            except ValueError:
                pass  # Ignore invalid input

        return queryset
