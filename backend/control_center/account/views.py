from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from .serializers import (
    UserSerializer, 
    ChangePasswordSerializer, 
    UserProfileSerializer,
    APIKeySerializer,
    APIKeyCreateSerializer,
    APIKeyResponseSerializer
)
from knox.auth import TokenAuthentication
from utils.api_key_utils import create_api_key
# views.py
from knox.models import AuthToken

# API View for Profile
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Keep user-only for security

    def get(self, request):
        user_serializer = UserSerializer(request.user)
        profile_serializer = UserProfileSerializer(request.user.profile)
        return Response({
            "user": user_serializer.data,
            "profile": profile_serializer.data
        })

    def put(self, request):
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        profile_serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)

        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            return Response({"message": "Profile updated successfully"})
        return Response({"errors": user_serializer.errors or profile_serializer.errors}, status=400)


# API View for Changing Password
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  # Keep user-only for security

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data["old_password"]):
                return Response({"error": "Old password is incorrect"}, status=400)

            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save()
            return Response({"message": "Password updated successfully"})

        return Response(serializer.errors, status=400)


class RefreshTokenView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user

        # Create a new token (this generates a new expiry automatically)
        instance, token = AuthToken.objects.create(user)

        # Optionally, delete the old token here if you want a one-to-one mapping

        return Response({
            "token": token,
            "expiry": instance.expiry  # instance.expiry is a datetime
        })

class Test401View(APIView):
    """
    A simple view that returns a 401 Unauthorized response.
    This can be used to simulate a session expiry.
    """
    def get(self, request, *args, **kwargs):
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


class APIKeyListView(APIView):
    """
    View for listing and creating API keys.
    
    GET: List all API keys (shows prefix, name, created date, revoked status)
    POST: Create a new API key (returns plaintext key once)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all API keys."""
        api_keys = APIKey.objects.all().order_by('-created')
        serializer = APIKeySerializer(api_keys, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new API key."""
        create_serializer = APIKeyCreateSerializer(data=request.data)
        if not create_serializer.is_valid():
            return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        name = create_serializer.validated_data['name']
        api_key, plaintext_key = create_api_key(name=name, revoked=False)
        
        # Construct response data directly to avoid serializer issues
        response_data = {
            'id': api_key.id,
            'api_key': plaintext_key,
            'prefix': api_key.prefix,
            'name': api_key.name,
            'created': api_key.created,
            'revoked': api_key.revoked,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class APIKeyDetailView(APIView):
    """
    View for retrieving and revoking API keys.
    
    GET: Get API key details (prefix only, never the full key)
    DELETE: Revoke an API key (sets revoked=True)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get API key details."""
        try:
            api_key = APIKey.objects.get(pk=pk)
        except APIKey.DoesNotExist:
            return Response(
                {"error": "API key not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = APIKeySerializer(api_key)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        """Revoke an API key."""
        try:
            api_key = APIKey.objects.get(pk=pk)
        except APIKey.DoesNotExist:
            return Response(
                {"error": "API key not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        api_key.revoked = True
        api_key.save()
        
        return Response(
            {"message": "API key revoked successfully"}, 
            status=status.HTTP_200_OK
        )