import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import time
from datetime import datetime
from wordcloud import WordCloud
import json
import os

NEWS_JSON_PATH = 'news_data/test.json'

def load_news_from_json():
    try:
        with open(NEWS_JSON_PATH, 'r', encoding='utf-8') as file:
            news_data = json.load(file)
        return news_data
    except FileNotFoundError:
        st.error("뉴스 데이터 파일을 찾을 수 없습니다.")
        return []
    except json.JSONDecodeError:
        st.error("뉴스 데이터 파일을 읽는데 오류가 발생했습니다.")
        return []

def display_news():
    st.title('News')

    # CSS for news box
    st.markdown("""
        <style>
        .news-box {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .news-box:hover {
            background-color: #f8f9fa;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .news-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .news-source {
            color: #666;
            font-size: 0.9em;
        }
        .news-date {
            color: #666;
            font-size: 0.9em;
        }
        .news-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #1a1a1a;
        }
        .news-content {
            color: #333;
            line-height: 1.5;
        }
        a {
            text-decoration: none;
            color: inherit;
        }
        a:hover {
            text-decoration: none;
            color: inherit;
        }
        </style>
    """, unsafe_allow_html=True)

    news_articles = load_news_from_json()

    if news_articles:
        for article in news_articles:
            # 각 뉴스 항목을 링크로 감싸기
            news_html = f"""
                <a href="{article['url']}" target="_blank">
                    <div class="news-box">
                        <div class="news-header">
                            <span class="news-source">{article['source_site']}</span>
                            <span class="news-date">{article['write_date']}</span>
                        </div>
                        <div class="news-title">{article['title']}</div>
                        <div class="news-content">{article['content']}</div>
                    </div>
                </a>
            """
            st.markdown(news_html, unsafe_allow_html=True)
    else:
        st.warning("크롤링한 뉴스가 없습니다.")

def run_mainPage():
    st.set_page_config(page_title="SSAFY News", layout="wide")
    
    # 사이드바에 네비게이션 링크 추가
    st.sidebar.title("Navigation")
    st.sidebar.page_link("mainPage.py", label="News")
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard")
    st.sidebar.page_link("pages/chatbotPage.py", label="ChatBot")
    
    display_news()

if __name__ == "__main__":
    run_mainPage()