"""
Serializers for recipe API endpoints.
"""
from rest_framework import serializers
from core.models import Ingredient, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects."""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price',
                  'description', 'link', 'tags')
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user

        for tag_data in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user, **tag_data
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create and return a new tag."""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validate_data):
        """Update and return an existing tag."""
        tags = validate_data.pop('tags', [])
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validate_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('user',)
        read_only_fields = RecipeSerializer.Meta.read_only_fields + ('user',)
