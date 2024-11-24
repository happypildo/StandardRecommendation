from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from .models import News, NewsSerializer, Keywords, KeywordSerializer, UserAction, UserActionSerializer

from .crawling.news_data_crawling import Crawler
from .crawling.extract_keywords import Extractor
from .crawling.summarize_gpt import Summarizer
from .crawling.link_to_standard_document import StringToWordConnection
from .crawling.link_to_standard_series import ExtractorRelationship, RAGInterestExtractor
from .chatbot.recommend import RAGRecommendation

import re
import json

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