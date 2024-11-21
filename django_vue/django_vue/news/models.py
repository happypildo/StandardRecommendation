from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
