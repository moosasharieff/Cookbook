"""
# app/recipe/serializers.py
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipes."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'price',
                  'time_minutes', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer to fetch single recipe details."""
    class Meta(RecipeSerializer.Meta):
        """Inherited attributes from `cls: RecipeSerializer`
        to build on this class."""
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only = ['id']
