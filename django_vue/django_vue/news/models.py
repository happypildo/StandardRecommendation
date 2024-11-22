from django.db import models
from django.conf import settings
from rest_framework import serializers
# from django.contrib.auth.models import User

User = settings.AUTH_USER_MODEL


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()


class Keywords(models.Model):
    keyword = models.CharField(max_length=50)
    intensity = models.FloatField(null=True)

    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='keywords')


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keywords
        fields = ['id', 'keyword', 'intensity']


class NewsSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'keywords']


class UserAction(models.Model):
    keyword = models.CharField(max_length=50)
    intensity = models.FloatField(null=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')


class UserActionSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)

    class Meta:
        model = UserAction
        fields = ["id", "keyword", "intensity", "keywords"]