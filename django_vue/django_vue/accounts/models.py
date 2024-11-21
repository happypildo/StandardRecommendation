from django.db import models
from django.contrib.auth.models import AbstractUser

# django 가 기본적으로 가진 auth 가 아닌
# accounts.User 를 회원 모델로 관리해야 한다.
class User(AbstractUser):
    # 추가하고 싶은 필드는 아래에 작성해주면 된다.
    nickname = models.CharField(max_length=100)