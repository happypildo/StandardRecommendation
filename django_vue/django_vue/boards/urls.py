from django.urls import path, include
from . import views

# 앱 네임스페이스 생성
app_name="boards"
urlpatterns = [
    # name: 경로를 직접 사용하지 않고,
    #   이름으로 쓰기 위해서 설정
    path('', views.board_list, name="board_list"),
    path('<int:pk>/', views.board_detail, name="board_detail"),# 상세 페이지 URL
    path('<int:board_pk>/comment/', views.add_comment, name="add_comment"),
    path('<int:board_pk>/favorite/', views.toggle_favorite, name="toggle_favorite"),
    # path('api/boards/', include('boards.urls')),
]
