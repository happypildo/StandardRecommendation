import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import ast

# 입력 및 출력 파일 경로
input_csv = "keywords_with_embeddings.csv"
output_csv = "kmeans_clustering_results.csv"

def read_csv_embeddings(file_path):
    """
    CSV 파일에서 키워드와 임베딩 데이터를 읽어옴
    """
    try:
        # CSV 읽기
        df = pd.read_csv(file_path)
        
        # 임베딩 컬럼을 리스트로 변환
        df['embedding'] = df['embedding'].apply(ast.literal_eval)  # 문자열 형태를 리스트로 변환
        
        return df
    
    except Exception as e:
        print("Error reading CSV:", str(e))
        return None

def perform_kmeans_clustering(embeddings, n_clusters=5, random_state=42):
    """
    K-Means를 사용하여 클러스터링 수행
    :param embeddings: 임베딩 벡터 리스트
    :param n_clusters: 생성할 클러스터 수
    :param random_state: 난수 시드 (결과 재현성을 위해 설정)
    :return: 각 데이터 포인트의 클러스터 레이블
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = kmeans.fit_predict(embeddings)
    return labels, kmeans.cluster_centers_

def save_clustering_results(df, labels, centers, output_file):
    """
    클러스터링 결과를 CSV로 저장
    :param df: 키워드 및 임베딩 데이터프레임
    :param labels: 클러스터 레이블 리스트
    :param centers: 클러스터 중심 좌표
    :param output_file: 저장할 파일 경로
    """
    try:
        # 클러스터 레이블 추가
        df['cluster'] = labels
        
        # 클러스터 중심 정보를 데이터프레임으로 저장
        centers_df = pd.DataFrame(centers, columns=[f"dim_{i}" for i in range(len(centers[0]))])
        centers_df["cluster"] = range(len(centers))
        
        # 결과 저장
        df.to_csv(output_file, index=False)
        print(f"KMeans clustering results saved to {output_file}")
        
        # 클러스터 중심 저장
        centers_file = output_file.replace(".csv", "_centers.csv")
        centers_df.to_csv(centers_file, index=False)
        print(f"Cluster centers saved to {centers_file}")
    
    except Exception as e:
        print("Error saving clustering results:", str(e))

# 1. CSV에서 키워드와 임베딩 읽기
df = read_csv_embeddings(input_csv)
if df is None or df.empty:
    print("No data to process. Exiting.")
    exit()

# 2. K-Means 클러스터링 수행
embeddings = np.array(df['embedding'].tolist())
n_clusters = 5  # 원하는 클러스터 개수 설정
labels, centers = perform_kmeans_clustering(embeddings, n_clusters=n_clusters)

# 3. 결과 저장
save_clustering_results(df, labels, centers, output_csv)
