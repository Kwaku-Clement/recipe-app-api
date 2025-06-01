"""
Test cases for the Django admin modification.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test.client import Client


class AdminTestCase(TestCase):
    """Test cases for the Django admin interface."""

    def setUp(self):
        """Set up the test case with a superuser."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_admin_user_list(self):
        """Test that the admin user list page is accessible."""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)
        # self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Users')
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.name)

    def test_admin_user_change_page(self):
        """Test that the admin user change page is accessible."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Change user')
        # self.assertContains(response, self.user.email)
        # self.assertContains(response, self.user.name)

    def test_admin_user_create_page(self):
        """Test that the admin user create page is accessible."""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
