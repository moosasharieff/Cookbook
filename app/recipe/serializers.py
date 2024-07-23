"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializers):
    """Serializers for recipes."""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'price', 'time_minutes', 'link']
        read_only_fields = ['id']