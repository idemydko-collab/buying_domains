from django.db import models
from django.contrib.auth.models import User


class Domain(models.Model):
    """Model for storing purchased domain information"""
    name = models.CharField(max_length=255, unique=True)
    zone = models.CharField(max_length=50)
    cloudflare_account_email = models.EmailField()
    cloudflare_zone_id = models.CharField(max_length=255, blank=True)
    registrar_domain_id = models.CharField(max_length=255, blank=True)
    keitaro_added = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


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