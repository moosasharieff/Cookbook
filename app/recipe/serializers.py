"""
# app/recipe/serializers.py
Serializers for recipe APIs.
"""
from typing import List

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
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'price',
                  'time_minutes', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, recipe: Recipe, tags: List[dict]) -> None:
        """Method fetches data from the db. If not found creates it."""
        auth_user = self.context['request'].user

        # Adding tags to the recipe
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data: dict) -> Recipe:
        """Modifying create() method to create recipe functionality."""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)

        # Adding tags to the recipe
        self._get_or_create_tags(recipe, tags)

        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Modifying update() method to update functionality to
        modify recipes."""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            # Update Tags to the recipe
            self._get_or_create_tags(instance, tags)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer to fetch single recipe details."""
    class Meta(RecipeSerializer.Meta):
        """Inherited attributes from `cls: RecipeSerializer`
        to build on this class."""
        fields = RecipeSerializer.Meta.fields + ['description']
