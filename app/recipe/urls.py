"""
# app/recipe/urls.py
URLs mappings for recipe app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagViewSet, IngredientViewSet, NutrientViewSet


router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('nutrients', NutrientViewSet)

app_name = 'recipe'

urlpatterns = [
        path('', include(router.urls)),
]
