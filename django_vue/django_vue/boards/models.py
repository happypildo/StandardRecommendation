from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Model -> serializer -> url -> view -> test
class Board(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    keyword = models.CharField((""), max_length=50)

# 댓글