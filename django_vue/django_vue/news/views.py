from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from .models import News, NewsSerializer, Keywords, KeywordSerializer, UserAction, UserActionSerializer

from .crawling.news_data_crawling import Crawler
from .crawling.extract_keywords import Extractor
from .crawling.summarize_gpt import Summarizer

import re

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
        print("In the view.py -------------------------------------")
        print(news)
        if not News.objects.filter(title=news['title']).exists():

            news_instance = News.objects.create(
                title=news['title'],
                content=news['contents']
            )
            
            ext_keywords = extractor.use_chat_gpt_for_extraction(content=news['contents'])
            print("Extracted keywords: ", ext_keywords)

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
    print("------------------------")
    print(request.user)
    print("------------------------")

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
    print("------------------------")
    print(request.user)
    print("------------------------")

    userKeywords = UserAction.objects.filter(user_id=request.user.id)
    userKeywords_serialized = UserActionSerializer(userKeywords, many=True)

    print(userKeywords_serialized.data)

    return Response(userKeywords_serialized.data)