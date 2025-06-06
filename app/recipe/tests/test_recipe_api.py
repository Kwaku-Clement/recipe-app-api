"""
Test cases for the recipe module.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag
from recipe.serializers import (RecipeSerializer,
                                RecipeDetailSerializer)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(**params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe name',
        'time_minutes': 20,
        'price': Decimal('5.99'),
        'description': 'Sample recipe description',
        'link': 'http://example.com/recipe.pdf',
        }
    defaults.update(params)
    recipe = Recipe.objects.create(**defaults)
    return recipe


def create_user(**params):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test the publicly unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the recipe endpoint."""
        response = self.client.get(RECIPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_recipes_limited_to_user(self):
        """Test list of recipes limited to unauthenticated user."""
        other_user = create_user(email='other@example.com',
                                 password='otherpass123')

        create_recipe(user=other_user)
        create_recipe(user=self.user)
        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test getting a recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'New Recipe',
            'time_minutes': 10,
            'price': Decimal('4.99'),
            'description': 'A new recipe description.',
            'link': 'http://example.com/new_recipe.pdf',
        }
        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe(self):
        """Test updating a recipe."""
        original_title = 'Original title'
        recipe = create_recipe(user=self.user, title=original_title)
        payload = {
            'title': 'Updated title',
            'time_minutes': 30,
            'price': Decimal('10.99'),
            'description': 'Updated description',
            'link': 'http://example.com/updated_recipe.pdf',
        }
        url = reverse('recipe:recipe-detail', args=[recipe.id])
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.title, 'Updated title')
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(user=self.user)
        url = reverse('recipe:recipe-detail', args=[recipe.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_partial_update_recipe(self):
        """Test partially updating a recipe."""
        original_link = 'http://example.com/original_recipe.pdf'
        recipe = create_recipe(user=self.user, link=original_link)
        payload = {'title': 'Partially Updated Title'}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test fully updating a recipe."""
        original_link = 'http://example.com/original_recipe.pdf'
        recipe = create_recipe(user=self.user,
                               title='Sample recipe Title',
                               description='Original description',
                               link=original_link)
        payload = {
            'title': 'Fully Updated Title',
            'time_minutes': 45,
            'price': Decimal('15.99'),
            'description': 'Fully updated description.',
            'link': 'http://example.com/fully_updated_recipe.pdf',
        }
        url = detail_url(recipe.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_user_raises_error(self):
        """Test updating recipe user raises error."""
        new_user = create_user(email='new@example.com',
                               password='newpass123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_other_user_recipe_raises_error(self):
        """Test deleting a recipe of another user raises error."""
        other_user = create_user(email='other@example.com',
                                 password='otherpass123')
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Continental Dish',
            'time_minutes': 20,
            'price': Decimal('5.99'),
            'description': 'New recipe description.',
        }
        tags = [{'name': 'Continental'}, {'name': 'Dinner'}]
        payload['tags'] = tags

        response = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recipe = recipe[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag_data in tags:
            exists = recipe.tags.filter(name=tag_data['name'],
                                        user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Indian Dish',
            'time_minutes': 60,
            'price': Decimal('10.99'),
            'description': 'A delicious Indian dish.',
        }
        tags = [{'name': 'Indian'}, {'name': 'Breakfast'}]
        payload['tags'] = tags

        response = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipes = recipes[0]
        self.assertEqual(recipes.tags.count(), 2)
        self.assertIn(tag_indian, recipes.tags.all())

        for tag_data in tags:
            exists = recipes.tags.filter(name=tag_data['name'],
                                         user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_launch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(tag_launch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='Dinner')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
        self.assertNotIn(tag, recipe.tags.all())
