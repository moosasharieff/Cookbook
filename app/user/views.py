"""
Views for the user API.
"""
from rest_framework import generics

from .serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    "Creates a new user in the system."
    # Defining the serializer to validate and store data.
    serializer_class = UserSerializer