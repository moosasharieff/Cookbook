"""
Views for the user API.
"""
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer



class CreateUserView(generics.CreateAPIView):
    "Creates a new user in the system."
    # Defining the serializer to validate and store data.
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Crate a new auth token for the user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
