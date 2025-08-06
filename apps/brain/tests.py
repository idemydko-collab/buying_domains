from django.test import TestCase
from django.contrib.auth.models import User
from .models import ExampleModel


class ExampleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
    def test_create_example(self):
        """Test creating an example model"""
        example = ExampleModel.objects.create(
            title='Test Example',
            description='This is a test example',
            created_by=self.user
        )
        
        self.assertEqual(example.title, 'Test Example')
        self.assertEqual(example.created_by, self.user)
        self.assertTrue(example.is_active)
        
    def test_example_str_method(self):
        """Test the string representation of ExampleModel"""
        example = ExampleModel.objects.create(
            title='Test Title',
            created_by=self.user
        )
        
        self.assertEqual(str(example), 'Test Title')