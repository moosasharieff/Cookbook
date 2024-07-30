"""
# app/recipe/serializers.py
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipes."""
    # Creating a nested serializer
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'price',
                  'time_minutes', 'link', 'tags']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Customizing create() to make sure we also include
        tags when creating a recipe."""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        # Fetch authorized user in serializer.py file
        auth_user = self.context['request'].user

        # Getting or Creating tags
        for tag in tags:
            # Return a tuple
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )

            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer to fetch single recipe details."""
    class Meta(RecipeSerializer.Meta):
        """Inherited attributes from `cls: RecipeSerializer`
        to build on this class."""
        fields = RecipeSerializer.Meta.fields + ['description']
