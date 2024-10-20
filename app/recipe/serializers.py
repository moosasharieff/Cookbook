"""
# app/recipe/serializers.py
Serializers for recipe APIs.
"""
from typing import List

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient, Nutrient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only = ['id']


class NutrientSerializer(serializers.ModelSerializer):
    """Serializer to convert data while sending and retrieving
    nutrient database information"""

    class Meta:
        model = Nutrient
        fields = ['id', 'name', 'grams']
        read_only = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer to convert data while sending and retrieving
    ingredient database information."""
    # Adding NutrientSerializer to retrieve nutrients when
    # creating, retrieving and updating Ingredients via API.
    nutrients = NutrientSerializer(many=True, required=False)

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'image', 'nutrients']
        read_only = ['id']

    def _get_or_create_nutrients(self, ingredient: Ingredient,
                                 nutrients: Nutrient) -> None:
        """Method fetches ingredient data from the db.
        If not found creates it."""
        auth_user = self.context['request'].user

        # Adding ingredients to the recipe
        for nutrient in nutrients:
            nutrient_obj, created = Nutrient.objects.get_or_create(
                user=auth_user,
                **nutrient
            )
            # Add nutrient's object to ingredient
            ingredient.nutrients.add(nutrient_obj)

    def create(self, validated_data: dict) -> Recipe:
        """Modifying create() method to create recipe functionality."""
        nutrients = validated_data.pop('nutrients', [])

        ingredient = Ingredient.objects.create(**validated_data)

        # Adding tags/ingredients to the recipe
        self._get_or_create_nutrients(ingredient, nutrients)

        return ingredient

    def update(self, instance: Ingredient, validated_data: dict) -> Ingredient:
        """Overriding update() method to update nutrients mapped
        inside ingredient."""
        nutrients = validated_data.pop('nutrients', [])

        if nutrients is not None:
            # Removing nutrients from ingredients
            instance.nutrients.clear()
            # Adding nutrients to ingredients
            self._get_or_create_nutrients(instance, nutrients)

        # Adding attr:values in validating data to ingredients
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'price',
                  'time_minutes', 'link', 'tags', 'ingredients']
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

    def _get_or_create_ingredients(self, recipe: Recipe,
                                   ingredients: Ingredient) -> None:
        """Method fetches ingredient data from the db.
        If not found creates it."""
        auth_user = self.context['request'].user

        # Adding ingredients to the recipe
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            # Add ingredient's object to recipe
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data: dict) -> Recipe:
        """Modifying create() method to create recipe functionality."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)

        # Adding tags/ingredients to the recipe
        self._get_or_create_tags(recipe, tags)
        self._get_or_create_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Overriding update() method to allow writing tags
         and ingredients to the recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            # Update Tags to the recipe
            self._get_or_create_tags(instance, tags)

        if ingredients is not None:
            instance.ingredients.clear()
            # Update ingredients to the recipe
            self._get_or_create_ingredients(instance, ingredients)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer to fetch single recipe details."""

    class Meta(RecipeSerializer.Meta):
        """Inherited attributes from `cls: RecipeSerializer`
        to build on this class."""
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only = ['id']
        extra_kwargs = {
            'image':
                {'required': 'True'},
        }


class IngredientImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to ingredient"""
    class Meta:
        model = Ingredient
        fields = ['id', 'image']
        read_only = ['id']
        extra_kwargs = {
            'image':
                {'required': 'False'},
        }
