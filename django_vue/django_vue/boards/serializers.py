from rest_framework import serializers
from .models import Board

# 게시글
# 1. 전체 게시글 조회
# 2. 게시글 생성
#   - 사용자 입력: 제목, 내용
#   - 자동 입력: 유저 정보
# ModelSerializer: DB 에 정의된 필드 안에서만 포장을 하고 싶을 때
# Serializer: DB 에 정의된 필드 말고도 포장을 하고 싶을 때
class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('id', 'title', 'content', 'writer',)
        read_only_fields = ('writer', )

# 3. 상세 게시글 (조회, 수정)
#   - 모든 필드 다 조회
class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'