"""
# app/recipe/serializers.py
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


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

    def _get_or_create_tags(self, recipe, tags):
        """Method to get or add new tags to the recipe."""
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

    def create(self, validated_data):
        """Customizing create() to make sure we also include
        tags when creating a recipe."""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)

        # Implement code to get or create tags in the recipe
        self._get_or_create_tags(recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        """Updating attributes of the recipe objects."""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            # Implement code for adding tags here
            instance.tags.clear()
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


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the Ingredients"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only = ['id']
