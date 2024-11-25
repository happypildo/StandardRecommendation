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

from langchain_community.embeddings import HuggingFaceEmbeddings

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class RAGInterestExtractor:
    def __init__(self, keywords, weights):
        self.keywords = keywords
        self.weights = weights

        sorted_items = sorted(zip(self.weights, self.keywords), reverse=True)

        self.top_weights = [weight for weight, _ in sorted_items[:5]]
        self.top_keywords = [keyword for _, keyword in sorted_items[:5]]

        self.keywords = [keyword for _, keyword in sorted_items[:15]]
        self.weights = [weight for weight, _ in sorted_items[:15]]

        connection_string = PGVector.connection_string_from_db_params(
            driver=os.getenv("DB_DRIVER", "psycopg2"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "backend"),
            user=os.getenv("DB_USER", "ssafy"),
            password=os.getenv("DB_PASSWORD", "1234")
        )

        embeddings = HuggingFaceEmbeddings(
            model_name='allenai/scibert_scivocab_uncased',
            model_kwargs={'device':'cpu'},
        )

        # 벡터 저장소 초기화
        self.vectorstore = PGVector(
            connection_string=connection_string,
            embedding_function=embeddings,
            collection_name="series_documents",
            # pre_delete_collection=True  # 기존 데이터를 삭제하고 새로 컬렉션 초기화
        )

    def extract(self, extracting_type=None):
        target_series_list = []
        if extracting_type is None:
            # target_series_list = [i for i in range(56)]
            target_series_list = [i for i in range(21, 39)]

            gathered_series = []
            gathered_scores = []
            for series in target_series_list:
                scores = []
                for keyword in self.top_keywords:
                    results = self.vectorstore.similarity_search_with_relevance_scores(
                        query=keyword,
                        k=3,
                        filter={"series": series}
                    )

                    scores_of_keyword = [r[-1] * (w ** 1) for r, w in zip(results, self.top_weights)]
                    sum_of_scores = sum(scores_of_keyword)
                    scores.append(sum_of_scores)
                
                if sum(scores) == 0:
                    continue
                else:
                    gathered_series.append(series)
                    gathered_scores.append([sum(scores)] + scores)
            
            sorted_items = sorted(zip(gathered_scores, gathered_series), reverse=True, key=lambda x: x[0][0])
            top_sorted_nodes = [series for _, series in sorted_items[:5]]
            top_sorted_similarities = [sim for sim, _ in sorted_items[:5]]

            nodes = self.top_keywords + [f'Series {s}' for s in top_sorted_nodes]
            nodes = [{"name": n} for n in nodes]
            links = []
            for node_off, similarities in enumerate(top_sorted_similarities):
                for k_idx, s in enumerate(similarities[1:]):
                    links.append({
                        'source': k_idx,
                        'target': len(self.top_keywords) + node_off,
                        'value': s
                    })
            
            data = {'nodes': nodes, 'links': links}
            return data
        else:
            target_series = extracting_type

            scores = []
            for keyword in self.keywords:
                results = self.vectorstore.similarity_search_with_relevance_scores(
                    query=keyword,
                    k=3,
                    filter={"series": target_series}
                )

                scores_of_keyword = [r[-1] * w for r, w in zip(results, self.top_weights)]
                sum_of_scores = sum(scores_of_keyword)
                scores.append(sum_of_scores)
            print(scores)
            nodes = []
            for k in self.keywords:
                nodes.append({
                    "id": k, "group": 1
                })
            nodes.append({
                "id": f"Series {target_series}"
            })

            links = []
            for idx, k in enumerate(self.keywords):
                links.append({
                    'source': k,
                    'target': f"Series {target_series}",
                    'weight': scores[idx] + 1e-9
                })
            
            data = {
                'nodes': nodes,
                'links': links
            }

            return data





series_descriptions = {
    1: "General aspects and principles of the GSM system.",
    2: "Service aspects of the GSM system.",
    3: "Network aspects and architecture of the GSM system.",
    4: "MS-BSS interface and protocol specifications.",
    5: "Physical layer on the radio path; General description.",
    6: "Speech codec specifications.",
    7: "Terminal adaptor for MS to public data networks.",
    8: "BSS-MSC interface and protocol specifications.",
    9: "Interworking between GSM and other networks.",
    10: "GSM public land mobile network (PLMN) connection types.",
    11: "Equipment and type approval specifications.",
    12: "Operation and maintenance aspects of the GSM system.",
    13: "Security-related network functions.",
    14: "GSM system enhancements.",
    15: "GSM data services.",
    16: "GSM mobile station (MS) features.",
    17: "GSM network features.",
    18: "GSM radio aspects.",
    19: "GSM speech processing.",
    20: "GSM data transmission.",
    21: "GSM signaling protocols.",
    22: "Service requirements for the UMTS system.",
    23: "Technical realization of service aspects.",
    24: "Signaling protocols and switching.",
    25: "Radio Access Network (RAN) aspects.",
    26: "Codecs and multimedia services.",
    27: "Data services and terminal interfaces.",
    28: "Signaling protocols and switching (continued).",
    29: "Core network protocols.",
    30: "Charging and billing.",
    31: "Security-related network functions.",
    32: "Telecommunication management; Charging management.",
    33: "Security aspects.",
    34: "UMTS test specifications.",
    35: "Security algorithms.",
    36: "Evolved Universal Terrestrial Radio Access (E-UTRA); LTE.",
    37: "Radio measurement and protocol aspects.",
    38: "NR (New Radio) access technology.",
    39: "Interworking between 3GPP and non-3GPP systems.",
    40: "Service aspects; Stage 2.",
    41: "General aspects and principles of the 3GPP system.",
    42: "Service aspects of the 3GPP system.",
    43: "Network aspects and architecture of the 3GPP system.",
    44: "MS-BSS interface and protocol specifications.",
    45: "Physical layer on the radio path; General description.",
    46: "Speech codec specifications.",
    47: "Terminal adaptor for MS to public data networks.",
    48: "BSS-MSC interface and protocol specifications.",
    49: "Interworking between 3GPP and other networks."
}
     


class ExtractorRelationship:
    def __init__(self, keywords, weights, model_name="bert-base-uncased"):
        print(f"Loading model '{model_name}'...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        print("Model loaded successfully!")

        self.keywords = keywords
        self.weights = weights

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze(0)
        return cls_embedding.numpy()

    def calculate_similarity(self):
        string_embedding = self.get_embedding(self.string)
        keyword_embeddings = [self.get_embedding(keyword) for keyword in self.keywords]

        similarities = []
        for idx, keyword_embedding in enumerate(keyword_embeddings):
            similarity = np.dot(string_embedding, keyword_embedding) / (
                np.linalg.norm(string_embedding) * np.linalg.norm(keyword_embedding) + 1e-9
            )
            similarities.append(similarity * self.weights[idx])

        return similarities
    
    def all_relationship(self):
        keyword_nodes = [{"name": keyword} for keyword in self.keywords]
        series_nodes = [{"name": f"Series {i}"} for i in range(1, 50)]
        
        links = []
        keyword_embeddings = [self.get_embedding(keyword) for keyword in self.keywords]

        all_similarities = []
        sum_similarities = []
        for series in range(1, 50):
            string = series_descriptions[series]

            string_embedding = self.get_embedding(string)

            similarities = []
            for idx, keyword_embedding in enumerate(keyword_embeddings):
                similarity = np.dot(string_embedding, keyword_embedding) / (
                    np.linalg.norm(string_embedding) * np.linalg.norm(keyword_embedding) + 1e-9
                )
                similarities.append(similarity * self.weights[idx])
            sum_similarities.append(sum(similarities).item())
            all_similarities.append(similarities[:])
        
        sorted_items = sorted(zip(sum_similarities, series_nodes, all_similarities), reverse=True, key=lambda x: x[0])
        top_series_nodes = [series for _, series, _ in sorted_items[:5]]
        top_similarities = [sim for _, _, sim in sorted_items[:5]]
        # print()
        # print()
        # print()
        # print("TOP SIMI")
        # print(sum_similarities)
        # print(sorted_items)
        # print(top_similarities)
        nodes = keyword_nodes + top_series_nodes
        for series, similarities in enumerate(top_similarities):
            for k_idx, sim in enumerate(similarities):
                links.append({
                        "source": k_idx,
                        "target": len(self.keywords) + series,
                        "value": sim.item()
                    })
        
        data = {
            'nodes': nodes,
            'links': links
        }

        return data

    def process(self, threshold=0.1):
        return self.all_relationship()


