from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from .models import News, NewsSerializer, Keywords, KeywordSerializer, UserAction, UserActionSerializer, TopKeywords, TopKeywordsSerializer

from .crawling.news_data_crawling import Crawler
from .crawling.extract_keywords import Extractor
from .crawling.summarize_gpt import Summarizer
from .crawling.link_to_standard_document import StringToWordConnection
from .crawling.link_to_standard_series import ExtractorRelationship, RAGInterestExtractor
from .chatbot.recommend import RAGRecommendation
from django.db.models import Sum, Count
import re
import json


def get_top_news_by_keyword(name):
    keywords = Keywords.objects.filter(keyword=name).order_by('-intensity')[:5]
    news_list = []
    for keyword in keywords:
        news_list.append({
            "title": keyword.news.title,
            "content": keyword.news.content[:100] + "..."
        })
    return news_list


@api_view(['GET'])
def get_news_trends(request):
    print("\n\n\n\n\n\n[Django news views.py] get_news_trends is called...")

    # 요청한 사용자 ID 가져오기
    user_id = request.user.id
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)

    # 1) 상위 10개의 키워드 가져오기
    top_keywords = TopKeywords.objects.order_by('-count')[:10]
    if not top_keywords.exists():
        return Response({"error": "No top keywords found"}, status=404)

    # 2) 사용자별 특정 키워드의 행 개수 계산 및 비율 계산
    results = []
    for top_keyword in top_keywords:
        keyword = top_keyword.keyword
        count = top_keyword.count

        # UserAction에서 사용자 ID와 키워드로 행 개수 계산
        user_action_count = UserAction.objects.filter(user_id=user_id, keyword=keyword).count()

        # 비율 계산
        ratio = user_action_count / count if count > 0 else 0
        ratio = min(ratio, 1)  # 비율은 최대 1로 제한

        # 결과 추가
        results.append({
            'name': keyword,
            'value': ratio
        })

    print(results)
    # 최종 결과 반환
    return Response(results)

@api_view(['POST'])
def rec_news(request):
    if request.method == 'POST':
        try:
            # 요청 본문에서 JSON 데이터 파싱
            body = json.loads(request.body)
            name = body.get('name', None)  # 'name' 값을 가져옴

            if name:
                # 여기서 name 기반으로 데이터를 처리
                news = get_top_news_by_keyword(name)
                return JsonResponse(news, safe=False)  # JSON 응답 반환
            else:
                return JsonResponse({"error": "name이 없습니다."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON 형식이 잘못되었습니다."}, status=400)
    else:
        return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)
    

@api_view(['GET'])
def news_list(request):
    if request.method == 'GET':
        news_obj = News.objects.all()
        serializer = NewsSerializer(news_obj, many=True)

        print(serializer.data)

        return Response(serializer.data)


@api_view(['GET'])
def news_list_update(request):
    crawler = Crawler()
    extractor = Extractor()

    for news in crawler.crawl_data():
        exclude_list = [r"3GPP", r"ETSI", r"TSG", r"WG\*", r"TCCA"]
        pattern = r'\b(' + '|'.join(exclude_list) + r')\b'
        if not News.objects.filter(title=news['title']).exists():

            news_instance = News.objects.create(
                title=news['title'],
                content=news['contents']
            )
            keywords = extractor.extract_keywords(news_content=news['contents'])
            for k, i in keywords:
                cleaned_keyword = re.sub(pattern, '', k)
                cleaned_keyword = re.sub(r'\s+', ' ', cleaned_keyword).strip()
                print(cleaned_keyword)
                Keywords.objects.create(news=news_instance, keyword=cleaned_keyword, intensity=i)
            
        else:
            break
        
    return Response({'message': "Good ^_^"})


@api_view(['GET'])
def news_summarize(request, id):
    summarizer = Summarizer()

    news = get_object_or_404(News, pk=id)
    news = NewsSerializer(news)

    message = summarizer.use_chat_gpt_for_summarization(
        title=news['title'],
        content=news['content']
    )

    keywords = Keywords.objects.filter(news_id=id)
    keywords_serialized = KeywordSerializer(keywords, many=True).data
    
    # 사용자와 키워드 연동하기
    for keyword in keywords:
        UserAction.objects.create(
            user=request.user,
            keyword=keyword.keyword,
            intensity=keyword.intensity
        )


    return Response({'message': message})

@api_view(['GET'])
def interest_info(request):
    print("\n\n\n\n\n\n[Django news views.py] interest_info is called...")
    userKeywords = UserAction.objects.filter(user_id=request.user.id)
    userKeywords_serialized = UserActionSerializer(userKeywords, many=True)
    print(userKeywords_serialized.data)

    return Response(userKeywords_serialized.data)

@api_view(['GET'])
def relation_series(request):
    userKeywords = UserAction.objects.filter(user_id=request.user.id)
    userKeywords_serialized = UserActionSerializer(userKeywords, many=True)

    keywords = []
    weights = []
    
    for data_dict in userKeywords_serialized.data:
        keywords.append(data_dict['keyword'])
        weights.append(data_dict['intensity'])

    kw_dict = {}
    for k, w in zip(keywords, weights):
        if kw_dict.get(k, None) is None:
            kw_dict[k] = w
        else:
            kw_dict[k] += w
    
    keywords = list(kw_dict.keys())
    weights = list(kw_dict.values())

    ext = RAGInterestExtractor(
        keywords=keywords,
        weights=weights,
        )
    output = ext.extract()

    return JsonResponse(output)

    

@api_view(['GET'])
def release_graph(request, series_num):
    userKeywords = UserAction.objects.filter(user_id=request.user.id)
    userKeywords_serialized = UserActionSerializer(userKeywords, many=True)

    keywords = []
    weights = []
    
    for data_dict in userKeywords_serialized.data:
        keywords.append(data_dict['keyword'].lower())
        weights.append(data_dict['intensity'])
    
    kw_dict = {}
    for k, w in zip(keywords, weights):
        if kw_dict.get(k, None) is None:
            kw_dict[k] = w
        else:
            kw_dict[k] += w
    
    keywords = list(kw_dict.keys())
    weights = list(kw_dict.values())

    ext = RAGInterestExtractor(
        keywords=keywords,
        weights=weights,
        )
    output = ext.extract(extracting_type=series_num)

    return JsonResponse(output)

@api_view(['POST'])
def chat(request):
    data = json.loads(request.body)
    user_message = data.get("message", "")

    rec = RAGRecommendation(user_message)
    bar_data, answer = rec.generate_answer()

    return JsonResponse({'data': answer, 'bar': bar_data})