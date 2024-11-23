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
from .crawling.link_to_standard_series import ExtractorRelationship

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

    sorted_items = sorted(zip(weights, keywords), reverse=True)

    top_weights = [weight for weight, _ in sorted_items[:5]]
    top_keywords = [keyword for _, keyword in sorted_items[:5]]

    ext = ExtractorRelationship(
        keywords=top_keywords,
        weights=top_weights,
        model_name="allenai/scibert_scivocab_uncased"
        )
    output = ext.all_relationship()
    print(output)
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

    stwc = StringToWordConnection(
        series_num=series_num,
        keywords=keywords,
        weights=weights,
        model_name="allenai/scibert_scivocab_uncased"
    )    

    # img = stwc.process()
    # # print(img)

    # return JsonResponse({'image': img})
    data = stwc.get_network_data()

    return JsonResponse(data)

@api_view(['POST'])
def chat(request):
    data = json.loads(request.body)
    user_message = data.get("message", "")

    return JsonResponse({'data': "Good"})