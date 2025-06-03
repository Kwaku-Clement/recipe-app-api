"""
Test for tag API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagApiTests(TestCase):
    """Test the publicly unavailable tag API request"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test the authorized user tag API request"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        respones = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(respones.status_code, status.HTTP_200_OK)
        self.assertEqual(respones.data, serializer.data)

    def tag_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        respones = self.client.get(TAG_URL)

        self.assertEqual(respones.status.code, status.HTTP_200_OK)
        self.assertEqual(len(respones.data), 1)
        self.assertEqual(respones.data[0]['name'], tag.name)
        self.assertEqual(respones.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
