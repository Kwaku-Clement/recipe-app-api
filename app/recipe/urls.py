"""
URL patterns for the recipe app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views
# Create a router and register the RecipeViewSet with it

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipe')
router.register('tags', views.TagViewSet, basename='tag')
router.register('ingredients', views.IngredientViewSet, basename='ingredient')


app_name = 'recipe'
urlpatterns = [
    path('', include(router.urls)),
]
