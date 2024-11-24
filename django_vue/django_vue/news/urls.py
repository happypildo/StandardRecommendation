from django.urls import path
from . import views

# 앱 네임스페이스 생성
app_name="news"
urlpatterns = [
    # name: 경로를 직접 사용하지 않고,
    #   이름으로 쓰기 위해서 설정
    path('list/', views.news_list, name='news_list'),
    path('renew/', views.news_list_update, name="news_list_update"),
    path('news_summarize/<int:id>/', views.news_summarize, name="news_summarize"),

    path('wcinfo/', views.interest_info, name="interest_info"),
    path('release_relation/<int:series_num>/', views.release_graph, name="release_graph"),
    path('relationship/', views.relation_series, name="relation_series"),
    path('chatbot/', views.chat, name="chat"),
    path('trends/', views.get_news_trends, name='get_news_trends'),
    path('lineplot/<str:keyword>/', views.others_trends, name='others_trends'),
]
