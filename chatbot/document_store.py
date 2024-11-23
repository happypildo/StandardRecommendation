from langchain.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
from Extractor import extract_information


class NewsDocumentStore:
    """
    뉴스 기사를 위한 문서 저장 및 검색 시스템
    PGVector를 백엔드로 사용하여 벡터 검색을 구현합니다.
    """

    def __init__(self):
        # 환경 변수 로드
        load_dotenv()

        # 데이터베이스 연결 문자열 생성
        self.connection_string = PGVector.connection_string_from_db_params(
            driver=os.getenv("DB_DRIVER", "psycopg2"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "vectordb"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )

        # 임베딩 모델 초기화
        self.embeddings = OpenAIEmbeddings()

        # 벡터 저장소 초기화
        self.vectorstore = PGVector(
            connection_string=self.connection_string,
            embedding_function=self.embeddings,
            collection_name="news_documents"
        )

    def process_news_article(self, article: Dict) -> Dict:
        # 본문 텍스트 처리
        print("-----------------------------------------")
        print(article)
        content = f"{article['title']}\n\n{article.get('area', '')}\n\n{article['scope']}\n\n{article['index']}"

        # 메타데이터 구성
        metadata = {
            'title': article['title'],
            'board': article.get('board', ''),
            'writer': article.get('writer', ''),
            'write_date': article.get('write_date', ''),
            'url': article.get('url', ''),
            'source_site': article.get('source_site', ''),
            'processed_date': datetime.now().isoformat()
        }

        return {
            'content': content,
            'metadata': metadata
        }

    def add_news_articles(self, articles: List[Dict]) -> None:
        documents = []
        for article in articles:
            try:
                processed = self.process_news_article(article)
                documents.append(
                    Document(
                        page_content=processed['content'],
                        metadata=processed['metadata']
                    )
                )
            except Exception as e:
                print("여기 입니까?", e)
                pass

        print(f"처리된 기사 개수: {len(documents)}")

        # 벡터 저장소에 문서 추가
        self.vectorstore.add_documents(documents)

    def similarity_search(self, query: str, k: int = 3, filter_dict: Optional[Dict] = None) -> List[Dict]:
        # 유사도 검색 수행
        docs = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=filter_dict
        )

        # 결과 포매팅
        results = []
        for doc, score in docs:
            results.append({
                'title': doc.metadata.get('title', ''),
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity': 1 - score  # 점수를 유사도로 변환
            })

        return results

    @classmethod
    def from_existing(cls, collection_name: str = "news_documents"):
        """
        기존 컬렉션을 사용하여 NewsDocumentStore 인스턴스를 생성합니다.

        Args:
            collection_name: 사용할 컬렉션 이름

        Returns:
            NewsDocumentStore 인스턴스
        """
        instance = cls()
        instance.vectorstore = PGVector(
            connection_string=instance.connection_string,
            embedding_function=instance.embeddings,
            collection_name=collection_name
        )
        return instance

    def delete_collection(self):
        """
        현재 컬렉션을 삭제합니다.
        """
        self.vectorstore.delete_collection()
        print(f"Collection '{self.vectorstore.collection_name}' has been deleted successfully.")