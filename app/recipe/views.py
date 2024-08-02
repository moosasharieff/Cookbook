"""
# app/recipe/view.py
Views for the recipe APIs.
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from .serializers import (RecipeSerializer,
                          RecipeDetailSerializer,
                          TagSerializer,
                          IngredientSerializer)


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

    def perform_create(self, serializer):
        """Create API for creating a new recipe."""
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin):
    """Manage tags in the database."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to output data for authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin):
    """Manage ingredients in the database"""
    serializer_class = IngredientSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # `var: queryset` is being called in `get_queryset()` method.
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        """
        By default, queryset return list of all the
        ingredients in the database. We customize this
        method to return only logged-in users ingredient list.
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')
