from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from .models import News, NewsSerializer, NewsKeywords

from .crawling.news_data_crawling import Crawler
from .crawling.extract_keywords import Extractor
from .crawling.summarize_gpt import Summarizer


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
            news = News.objects.create(
                title=news['title'],
                content=news['contents']
            )
            
            keywords = extractor.use_chat_gpt_for_extraction(content=news['contents'])
            for keyword in keywords.split(','):
                NewsKeywords.objects.create(news=news, keyword=keyword)
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

    return Response({'message': message})
