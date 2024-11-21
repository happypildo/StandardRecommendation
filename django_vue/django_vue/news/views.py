from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .models import News

from .crawling.news_data_crawling import Crawler
from .crawling.summarize_gpt import Summarizer


# 게시글 생성(POST), 전체 게시글 조회(GET)
@api_view(['GET'])
def news_list(request):
    crawler = Crawler()
    summarizer = Summarizer()

    for news in crawler.crawl_data():
        print("In the view.py -------------------------------------")
        print(news)
        if not News.objects.filter(title=news['title']).exists():
            News.objects.create(
                title=news['title'],
                content=news['contents']
            )
        message = summarizer.use_chat_gpt_for_summarization(
            title=news['title'],
            content=news['contents']
        )
        print("Summarization: ")
        print(message)
        

        
    
    return JsonResponse()