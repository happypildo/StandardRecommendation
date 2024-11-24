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
from django.db.models import Sum
import re
import json


@api_view(['GET'])
def get_news_trends(request):
    print("[Django news views.py] get_news_trends is called...")
    
    user_id = request.user.id  # 요청한 사용자의 ID
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)
    
    # 상위 10개의 키워드 가져오기
    top_keywords = TopKeywords.objects.order_by('-count')[:10]
    serializer = TopKeywordsSerializer(top_keywords, many=True)
    top_keywords_data = serializer.data
    # 키워드별 num_of_clicks 및 비율 계산
    results = []
    for keyword_data in top_keywords_data:
        keyword = keyword_data['keyword']
        count = keyword_data['count']

        # 해당 사용자와 키워드에 대한 num_of_clicks 가져오기
        user_action = UserAction.objects.filter(user_id=user_id, keyword=keyword).aggregate(total_clicks=Sum('num_of_clicks'))
        num_of_clicks = user_action['total_clicks'] or 0  # None 방지

        # 비율 계산
        ratio = num_of_clicks / count if count > 0 else 0
        ratio = ratio if ratio < 1 else 1
        # results.append({
        #     "keyword": keyword,
        #     "count": count,
        #     "num_of_clicks": num_of_clicks,
        #     "ratio": ratio,
        # })
        results.append({
            'name': keyword,
            'value': ratio
        })

    return Response(results)

@api_view(['GET'])
def others_trends(request, keyword):
    try:
        # 요청한 사용자의 ID
        current_user_id = request.user.id

        # 사용자별 특정 키워드의 클릭 횟수 합산
        user_clicks = (
            UserAction.objects.filter(keyword=keyword)
            .values('user_id')  # 사용자 ID별로 그룹화
            .annotate(total_clicks=Sum('num_of_clicks'))  # 클릭 횟수 합산
            .order_by('-total_clicks')  # 클릭 횟수 기준 내림차순 정렬
        )
        
        # 사용자 정보를 추가하여 데이터 구성
        user_ids = [user_click['user_id'] for user_click in user_clicks]

        data = [
            {
                "user_id": user_click['user_id'],
                "total_clicks": user_click['total_clicks'] or 0,  # 클릭 수가 없으면 0
                "is_current_user": user_click['user_id'] == current_user_id,  # 요청한 사용자와 동일 여부
            }
            for user_click in user_clicks
        ]
        data.append({
            "user_id": 2,
            "total_clicks": 5,
            "is_current_user": False
        })
        data.append({
            "user_id": 3,
            "total_clicks": 10,
            "is_current_user": False
        })
        data.append({
            "user_id": 4,
            "total_clicks": 40,
            "is_current_user": False
        })

        return JsonResponse(data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@api_view(['GET'])
def news_list(request):
    print("Called...")
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
        # print("In the view.py -------------------------------------")
        # print(news)
        if not News.objects.filter(title=news['title']).exists():

            news_instance = News.objects.create(
                title=news['title'],
                content=news['contents']
            )
            
            ext_keywords = extractor.use_chat_gpt_for_extraction(content=news['contents'])
            # print("Extracted keywords: ", ext_keywords)

            ext_keywords = ext_keywords.replace('\n', '')
            ext_keywords = ext_keywords.strip()

            keywords = []
            intensities = []
            for temp in ext_keywords.split('/'):
                if temp == "": break
                keyword, intensity = temp.split(',')
                keywords.append(keyword)
                intensities.append(intensity)
            
            intensities = [float(x) for x in intensities]
            intensities = [x / sum(intensities) for x in intensities]
            for k, i in zip(keywords, intensities):
                Keywords.objects.create(news=news_instance, keyword=k, intensity=i)
        else:
            break
        
    return Response({'message': "Good ^_^"})


@api_view(['GET'])
def news_summarize(request, id):
    # print("------------------------")
    # print(request.user)
    # print("------------------------")

    # news_id를 기반으로 키워드를 일단 가져오기
    # 키워드를 request.user로 연동하기

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

    print("\n\n\nTEST -------------------------")
    ext = RAGInterestExtractor(
        keywords=keywords,
        weights=weights,
        )
    output = ext.extract()
    from pprint import pprint
    pprint(output)

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

    print("\n\n\nTEST -------------------------")
    ext = RAGInterestExtractor(
        keywords=keywords,
        weights=weights,
        )
    output = ext.extract(extracting_type=series_num)
    from pprint import pprint
    pprint(output)

    return JsonResponse(output)

@api_view(['POST'])
def chat(request):
    print("-" * 20)
    data = json.loads(request.body)
    user_message = data.get("message", "")

    rec = RAGRecommendation(user_message)
    bar_data, answer = rec.generate_answer()

    return JsonResponse({'data': answer, 'bar': bar_data})