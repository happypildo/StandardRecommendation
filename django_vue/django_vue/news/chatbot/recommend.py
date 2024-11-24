import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import io
import base64

import os
import openai
import psycopg2
import numpy as np
from langchain.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class RAGRecommendation:
    def __init__(self, query):
        self.query = query
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
            streaming=True  # 스트리밍 활성화
        )

        connection_string = PGVector.connection_string_from_db_params(
            driver=os.getenv("DB_DRIVER", "psycopg2"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "backend"),
            user=os.getenv("DB_USER", "ssafy"),
            password=os.getenv("DB_PASSWORD", "1234")
        )

        embeddings = HuggingFaceEmbeddings(
            model_name='pritamdeka/S-BioBert-snli-multinli-stsb',
            model_kwargs={'device':'cpu'},
        )

        # 벡터 저장소 초기화
        self.vectorstore = PGVector(
            connection_string=connection_string,
            embedding_function=embeddings,
            collection_name="series_documents",
            # pre_delete_collection=True  # 기존 데이터를 삭제하고 새로 컬렉션 초기화
        )

    def generate_answer(self):
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query=self.query,
            k=3,
            # filter={"series": self.target_series}
        )

        system_prompt = """
        당신은 사용자의 질문에 대해 친절하고 전문적으로 답변하는 AI 어시스턴트입니다.
        제공된 문서 정보를 바탕으로 사용자에게 문서를 추천해 주세요.
        추천과 동시에 추천의 이유도 자세히 작성하길 바랍니다.
        답변은 한국어로 하되, 전문적이면서도 이해하기 쉽게 작성하세요.
        """

        bar_data = []
        context = "관련 문서 정보: \n"
        for i, result in enumerate(results):
            doc, score = result

            context += f"{i}. {doc.page_content}\n\n"
            bar_data.append({
                'label': doc.metadata['title'],
                'value': score
            })
        print(bar_data)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"다음 문서 정보를 참고하여 질문에 답변해주세요.\n\n{context}\n\n질문: {self.query}")
        ]
        
        answer = ""
        try:
            # GPT로 스트리밍 답변 생성 (invoke 메소드 사용)
            response = self.llm(
                messages,
            )
            answer = response.content
        except Exception as e:
            print(e)
            answer = "죄송합니다. 답변을 생성하는 중에 문제가 발생했습니다."

        return bar_data, answer


