# from rest_framework.authentication import TokenAuthentication
# from rest_framework.exceptions import AuthenticationFailed

# class QueryParameterTokenAuthentication(TokenAuthentication):
#     def authenticate(self, request):
#         # Check if the token is provided in the query parameter
#         token_key = request.GET.get('token')

#         if token_key:
#             return self.authenticate_credentials(token_key)
        
#         return None  # Use default authentication method


from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed



class QueryParamAuthenticationMixin:
    def get_token_from_query_params(self, request):
        return request.GET.get('token')
 
 
class QueryParameterTokenAuthentication(TokenAuthentication, JWTAuthentication, QueryParamAuthenticationMixin):
    
    def authenticate(self, request):
        # Extract token from query parameters
        token = self.get_token_from_query_params(request)
        if not token:
            return None
        
        # Single function to try both authentication methods
        return self._authenticate_token(token)

    def _authenticate_token(self, token):
        """
        Try to authenticate using JWT first, then fallback to regular TokenAuthentication.
        """
        # Attempt JWT Authentication
        try:
            validated_token = self.get_validated_token(token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed:
            pass  # JWT authentication failed, move to Token authentication

        # Attempt Token Authentication
        try:
            return self.authenticate_credentials(token)
        except AuthenticationFailed:
            raise AuthenticationFailed("Invalid token for both JWT and Token authentication.")