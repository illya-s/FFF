from django.db import models

# Create your models here.
class SocialNetwork(models.Model):
    name = models.CharField(max_length=100)
    icon_svg = models.TextField(help_text="Inline SVG")
    url = models.URLField()

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name