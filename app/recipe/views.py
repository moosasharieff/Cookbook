"""
# app/recipe/view.py
Views for the recipe APIs.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient, Nutrient
from .serializers import (RecipeSerializer,
                          RecipeDetailSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          NutrientSerializer,
                          RecipeImageSerializer,
                          IngredientImageSerializer)

from drf_spectacular.utils import (extend_schema_view,
                                   extend_schema,
                                   OpenApiParameter,
                                   OpenApiTypes)


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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma seperated list of Tag IDs '
                            'to filter recipes.'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma seperated list of Ingredient IDs '
                            'to filter recipes.'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing Recipe API."""
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Fetch all data from Recipe object
    queryset = Recipe.objects.all()

    def _params_to_ints(self, params: str) -> list[int]:
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in params.split(',')]

    def get_queryset(self) -> queryset:
        """Return recipes for authenticated user only.
        We are also able to filter the recipe based on the tags
        and ingredients.
        """
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return serializer class for list or detail request."""
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create API for creating a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in database."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == 'upload_image':
            return IngredientImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """API for creating new ingredient."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image to INGREDIENT."""
        ingredient = self.get_object()
        serializer = self.get_serializer(ingredient, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NutrientViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,):
    """Manages Nutrients in database."""
    serializer_class = NutrientSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Nutrient.objects.all()

    def get_queryset(self):
        """Overriding this method to retrieve only
        authenticated user data for nutrients."""
        return Nutrient.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create API for creating a new nutrient."""
        serializer.save(user=self.request.user)
