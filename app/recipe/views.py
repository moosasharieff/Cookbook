"""
# app/recipe/view.py
Views for the recipe APIs.
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient, Nutrient
from .serializers import (RecipeSerializer,
                          RecipeDetailSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          NutrientSerializer)


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin):
    """Class to be inherited by any class which needs to get
    associated with the recipe API."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to output data for authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


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


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in database."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def perform_create(self, serializer):
        """API for creating new ingredient."""
        serializer.save(user=self.request.user)


class NutrientViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,):
    """Manages Nutrients in database."""
    serializer_class = NutrientSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Nutrient.objects.all()

    def get_queryset(self):
        """Overriding this method to retrieve only
        authenticated user data for nutrients."""
        return Nutrient.objects.filter(user=self.request.user)
