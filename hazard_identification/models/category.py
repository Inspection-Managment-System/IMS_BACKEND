from django.db import models


class HazardCategory(models.Model):
    """Categories for different types of hazards"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6B7280', help_text="Hex color code for UI display")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or name for UI display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hazard Category"
        verbose_name_plural = "Hazard Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
