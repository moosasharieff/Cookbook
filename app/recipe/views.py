"""
# app/recipe/view.py
Views for the recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing Recipe API."""
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Fetch all data from Recipe object
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Return recipes for authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return serializer class for list or detail request."""
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class
