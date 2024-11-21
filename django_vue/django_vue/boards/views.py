from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.http import JsonResponse

from .serializers import BoardListSerializer, BoardSerializer
from .models import Board


# 게시글 생성(POST), 전체 게시글 조회(GET)
@api_view(['GET', 'POST'])
def board_list(request):
    if request.method == 'POST':
        # 사용자로부터 받은 입력을 포장
        serializer = BoardListSerializer(data=request.data)
        # 포장된 데이터가 모두 정상적일 때(유효성 검증을 통과했을 때),
        if serializer.is_valid():
            # 사용자 입력이 아닌 다른 필드들을 함께 저장하도록 코드를 구성
            serializer.save(writer=request.user)
            return Response(serializer.data)
    else:
        boards = Board.objects.all().order_by('-pk')
        serializer = BoardListSerializer(boards, many=True)
        return Response(serializer.data)
