from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('boards.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('dj-rest-auth/logout/', include('dj_rest_auth.urls')),
    path('api/boards/', include('boards.urls')),
    path('crawl/', include('news.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
