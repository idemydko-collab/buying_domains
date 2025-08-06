from django.db import models
from django.contrib.auth.models import User


class ExampleModel(models.Model):
    """Example model for demonstrating the Django setup"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='examples')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Example"
        verbose_name_plural = "Examples"
        ordering = ['-created_at']

    def __str__(self):
        return self.title