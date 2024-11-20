import json
import random
import time
from datetime import datetime
import os
from hdfs import InsecureClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lit, to_timestamp
from pyspark.sql.types import StringType, ArrayType, FloatType, StructType, StructField
import requests
from dotenv import load_dotenv
import threading
from openai import OpenAI

load_dotenv()

# HDFS 설정
hdfs_client = InsecureClient('http://localhost:9870', user='hadoop-user')
hdfs_path = '/user/news/realtime/'

# Spark 설정
SOURCE_DATA_PATH = f"hdfs://localhost:9000/user/news/realtime"
SOURCE_ARCHIVE_PATH = f"hdfs://localhost:9000/news_archive"

# 데이터 소스 경로
base_directory = '/home/ssafy/pjt08/training_raw_data'

# OpenAI 클라이언트 초기화
client = OpenAI()

def load_json_files_and_merge(base_directory, max_files_per_category=10):
    """
    데이터 소스 경로에 있는 모든 JSON 파일을 읽어와서 하나의 리스트로 병합
    """
    all_data = []

    for category in os.listdir(base_directory):
        category_path = os.path.join(base_directory, category)
        
        if os.path.isdir(category_path):
            print(f"카테고리 처리 중: {category}")
            file_count = 0
            for json_file in os.listdir(category_path):
                if json_file.endswith('.json') and file_count < max_files_per_category:
                    file_path = os.path.join(category_path, json_file)
                    
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        
                        if 'SJML' in data and 'text' in data['SJML']:
                            for text_item in data['SJML']['text']:
                                text_item['category'] = category
                                all_data.append(text_item)
                    
                    file_count += 1
                
                if file_count >= max_files_per_category:
                    break
    
    return all_data

def crawling_process():
    merged_data_list = load_json_files_and_merge(base_directory, 1)
    if not isinstance(merged_data_list, list):
        merged_data_list = list(merged_data_list)  # 리스트가 아니라면 리스트로 변환
    data_list = random.sample(merged_data_list, min(200, len(merged_data_list)))
    print(f"총 {len(data_list)}개의 뉴스 데이터를 처리합니다.")

    for data in data_list:
        json_data = json.dumps(data, ensure_ascii=False)
        base_file_name = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_name = base_file_name
        file_index = 1
        while hdfs_client.status(hdfs_path + file_name, strict=False):
            file_name = f"{base_file_name[:-5]}_{file_index}.json"
            file_index += 1

        with hdfs_client.write(hdfs_path + file_name, encoding='utf-8') as writer:
            writer.write(json_data)
        
        print(f"Data sent to HDFS: {hdfs_path + file_name}")
        time.sleep(1)

def initialize_spark_session():
    return SparkSession.builder.appName("RealTimeNewsETL").getOrCreate()

def define_source_schema():
    return StructType([
        StructField("title", StringType(), True),
        StructField("source_site", StringType(), True),
        StructField("write_date", StringType(), True),
        StructField("content", StringType(), True),
        StructField("url", StringType(), True)
    ])

def create_source_stream(spark, schema):
    return spark.readStream.schema(schema).option("cleanSource", "archive").option("sourceArchiveDir", SOURCE_ARCHIVE_PATH).json(SOURCE_DATA_PATH)

def transform_extract_keywords(text):
    text = preprocess_content(text)
    client = OpenAI()  # 함수 내부에서 클라이언트 생성
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 텍스트에서 주요 키워드를 추출하는 전문가입니다. 다음 텍스트에서 가장 중요한 5개의 키워드를 추출해주세요. 키워드는 쉼표로 구분하여 반환해주세요"},
            {"role": "user", "content": text}
        ],
        max_tokens=100
    )
    keywords = response.choices[0].message.content.strip()
    return keywords.split(',')

def transform_to_embedding(text: str) -> list[float]:
    text = preprocess_content(text)
    client = OpenAI()  # 함수 내부에서 클라이언트 생성
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def transform_classify_category(content):
    content = preprocess_content(content)
    client = OpenAI()  # 함수 내부에서 클라이언트 생성
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 뉴스 기사의 카테고리를 분류하는 어시스턴트입니다. No verbose. 카테고리는 [\"IT_과학\", \"건강\", \"경제\", \"교육\", \"국제\", \"라이프스타일\", \"문화\", \"사건사고\", \"사회일반\", \"산업\", \"스포츠\", \"여성복지\", \"여행레저\", \"연예\", \"정치\", \"지역\", \"취미\"] 중 하나입니다. 이외의 카테고리는 없습니다."},
            {"role": "user", "content": content}
        ]
    )
    model_output = response.choices[0].message.content.strip()
    if "카테고리:" in model_output:
        model_output = model_output.split("카테고리:")[1].strip()
    model_output = model_output.replace('"', '').replace("'", "").strip()
    return model_output

def preprocess_content(content):
    import tiktoken
    if not content:
        return ""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)
    return content

def register_transformation_udfs():
    return {
        "keywords": udf(transform_extract_keywords, ArrayType(StringType())),
        "embedding": udf(transform_to_embedding, ArrayType(FloatType())),
        "category": udf(transform_classify_category, StringType())
    }

def transform_dataframe(source_df, transformation_udfs):
    return source_df.withColumn("write_date", to_timestamp(col("write_date"), "yyyy-MM-dd HH:mm:ss")) \
             .withColumn("keywords", transformation_udfs["keywords"](col("content"))) \
             .withColumn("embedding", transformation_udfs["embedding"](col("content"))) \
             .withColumn("category", transformation_udfs["category"](col("content"))) \
             .withColumn("writer", col("source_site")) \
             .drop("source_site")

def load_to_target(batch_df, epoch_id):
    batch_df = batch_df.withColumn("keywords", col("keywords").cast(StringType())) \
                       .withColumn("embedding", col("embedding").cast(StringType()))
    batch_df.write.mode("append").parquet("realtime.parquet")

def start_etl_pipeline(transformed_df):
    query = transformed_df.writeStream \
        .foreachBatch(load_to_target) \
        .start()
    return query

def spark_streaming_process():
    spark = initialize_spark_session()
    source_schema = define_source_schema()
    source_stream = create_source_stream(spark, source_schema)
    transformation_udfs = register_transformation_udfs()
    transformed_df = transform_dataframe(source_stream, transformation_udfs)
    query = start_etl_pipeline(transformed_df)
    query.awaitTermination()

def main():
    # 크롤링 프로세스 실행
    crawling_process()

    # Spark 스트리밍 프로세스 실행
    spark_streaming_process()

if __name__ == "__main__":
    main()