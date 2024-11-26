from django.db import models
from django.conf import settings
from django.contrib.auth.models import User  # User 모델 임포트
User = settings.AUTH_USER_MODEL

# Model -> serializer -> url -> view -> test
class Board(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    # writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    keyword = models.CharField("키워드", max_length=50)

# 댓글
class Comment(models.Model):
    board = models.ForeignKey(Board, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user 필드 추가
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# 즐겨찾기 모델
class Favorite(models.Model):
    board = models.ForeignKey(Board, related_name="favorites", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="favorites", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)