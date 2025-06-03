"""
Views for the recipe API endpoints.
"""
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from recipe import serializers
from core.models import Recipe, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return recipes for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update an existing recipe."""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Delete a recipe."""
        instance.delete()


class TagViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tags for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
