from django.urls import path, include
from rest_framework import routers
from dj_rest_auth.views import LoginView, LogoutView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT 토큰 받기
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신
    path('dj-rest-auth/login/', LoginView.as_view(), name='rest_login'),  # 로그인
    path('dj-rest-auth/logout/', LogoutView.as_view(), name='rest_logout'),  # 로그아웃
    path('dj-rest-auth/registration/', RegisterView.as_view(), name='rest_register'),  # 회원가입

    # 다른 앱에 대한 URL 설정
    path('api-auth/', include('rest_framework.urls')),  # DRF 기본 인증
]