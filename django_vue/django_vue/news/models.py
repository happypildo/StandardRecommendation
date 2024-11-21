from django.db import models
from django.conf import settings
from rest_framework import serializers

User = settings.AUTH_USER_MODEL


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'