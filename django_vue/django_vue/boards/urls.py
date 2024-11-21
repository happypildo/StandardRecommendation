from django.urls import path
from . import views

# 앱 네임스페이스 생성
app_name="boards"
urlpatterns = [
    # name: 경로를 직접 사용하지 않고,
    #   이름으로 쓰기 위해서 설정
    path('', views.board_list, name="board_list"),
]
