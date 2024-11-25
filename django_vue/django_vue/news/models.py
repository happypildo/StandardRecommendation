from django.db import models
from django.conf import settings
from rest_framework import serializers
# from django.contrib.auth.models import User

User = settings.AUTH_USER_MODEL


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()


class Keywords(models.Model):
    keyword = models.TextField()
    intensity = models.FloatField(null=True)

    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='keywords')


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keywords
        fields = ['id', 'keyword', 'intensity']


class TopKeywords(models.Model):
    keyword = models.TextField(unique=True)  # 키워드는 고유하게 저장
    count = models.PositiveIntegerField(default=0)  # 등장 횟수


class TopKeywordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopKeywords
        fields = ['keyword', 'count']  # 반환할 필드
        

class NewsSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'keywords']


class UserAction(models.Model):
    keyword = models.TextField()
    intensity = models.FloatField(null=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')


class UserActionSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)

    class Meta:
        model = UserAction
        fields = ["id", "keyword", "intensity", "keywords"]

