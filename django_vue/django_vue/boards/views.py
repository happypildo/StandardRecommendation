from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .serializers import BoardListSerializer, BoardSerializer, CommentSerializer
from .models import Board, Favorite, Comment

@api_view(['GET', 'POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def board_list(request):
    if request.method == 'POST':
        print(f"User authenticated: {request.user.is_authenticated}")  # 디버깅 로그
        print(f"User: {request.user}")  # 사용자 정보 로그
        serializer = BoardListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    else:
        boards = Board.objects.all().order_by('-pk')
        serializer = BoardListSerializer(boards, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def board_detail(request, pk):
    board = get_object_or_404(Board, pk=pk)
    serializer = BoardSerializer(board)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_comment(request, board_pk):
    try:
        board = get_object_or_404(Board, pk=board_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=request.user, board=board)
            return Response(serializer.data, status=201)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=400)
    except Exception as e:
        print("Exception:", str(e))
        return Response({'error': str(e)}, status=500)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, board_pk):
    try:
        board = get_object_or_404(Board, pk=board_pk)
        
        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(board=board, user=request.user)
            if created:
                return Response({"message": "게시글이 즐겨찾기에 추가되었습니다."}, status=201)
            else:
                return Response({"message": "이미 즐겨찾기에 추가된 게시글입니다."}, status=200)

        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(board=board, user=request.user).first()
            if favorite:
                favorite.delete()
                return Response({"message": "게시글이 즐겨찾기에서 삭제되었습니다."}, status=200)
            else:
                return Response({"message": "즐겨찾기에 존재하지 않는 게시글입니다."}, status=404)

    except Exception as e:
        print("Exception:", str(e))
        return Response({'error': str(e)}, status=500)