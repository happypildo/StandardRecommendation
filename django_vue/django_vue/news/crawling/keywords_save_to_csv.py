import os
import csv
import psycopg2
from sentence_transformers import SentenceTransformer

# PostgreSQL 연결 설정
connection_string = f"""
    host={os.getenv("DB_HOST", "localhost")}
    port={os.getenv("DB_PORT", "5432")}
    dbname={os.getenv("DB_NAME", "backend")}
    user={os.getenv("DB_USER", "ssafy")}
    password={os.getenv("DB_PASSWORD", "1234")}
"""

# CSV 파일 저장 경로
output_csv = "keywords_with_embeddings.csv"

# 임베딩 모델 초기화
model_name = "allenai/scibert_scivocab_uncased"
embedding_model = SentenceTransformer(model_name)

def fetch_keywords():
    """
    PostgreSQL에서 news_topkeywords 테이블의 keyword 컬럼을 가져옴
    """
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        # SQL 쿼리 실행
        query = "SELECT keyword FROM news_topkeywords;"
        cursor.execute(query)
        keywords = cursor.fetchall()  # 결과 가져오기

        # 결과 반환 (2차원 튜플을 1차원 리스트로 변환)
        return [row[0] for row in keywords]

    except Exception as e:
        print("Error fetching data:", str(e))
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_embeddings_to_csv(keywords):
    """
    주어진 키워드를 임베딩하고 결과를 CSV로 저장
    """
    try:
        # CSV 파일 열기
        with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            
            # 헤더 작성
            writer.writerow(["keyword", "embedding"])

            # 키워드 임베딩 생성 및 저장
            for keyword in keywords:
                embedding = embedding_model.encode(keyword).tolist()  # 임베딩 생성 및 리스트로 변환
                writer.writerow([keyword, embedding])
        
        print(f"Embeddings saved to {output_csv}")
    
    except Exception as e:
        print("Error saving embeddings:", str(e))

# 1. 키워드 가져오기
keywords = fetch_keywords()
if not keywords:
    print("No keywords fetched. Exiting.")
    exit()

# 2. 키워드 임베딩 및 저장
save_embeddings_to_csv(keywords)
