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

class NewsKeywords(models.Model):
    keyword = models.CharField(max_length=50)

    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='news_set')