# import json
# from openai import OpenAI
# import os

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# client = OpenAI(api_key=OPENAI_API_KEY)


# class Extractor:
#     def __init__(self, model='gpt-4o-mini'):
#         self.model = model

#     def chat_completion_request(self, messages):
#         try:
#             response = client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 # tools=self.tools,
#             )
#             return response
#         except Exception as e:
#             print("Unable to generate ChatCompletion response")
#             print(f"Exception: {e}")
#             return e

#     def make_message(self, user_msg):
#         msg = [
#             {"role": "system", "content": "당신은 사용자 요청 답변하는 챗봇입니다."},
#             {"role": "system", "content": "당신은 무선 및 유선 통신에서의 전문가입니다."},
#             {"role": "system", "content": "입력으로 받는 정보 중 `content`는 뉴스는 이동통신 관련 단체들 간의 공동 연구 프로젝트로 국제전기통신연합(ITU)의 IMT-2000 프로젝트의 범위 내에서 - 전 세계적으로 적용 가능한 - 3세대 이동통신 시스템 규격의 작성을 목적으로 하는 3GPP 단체에서 발행한 기사입니다."},
#             {"role": "system", "content": """
#             해당 뉴스에서 중요한 3가지 요소를 출력하세요.
#             # 중요: 최소 1개에서 최대 3개까지의 요소를 출력하세요.
#             # 중요: 해당 뉴스를 발간한 기관인 3GPP와 유선 및 무선 통신에 관련된 키워드로 구성하세요.
#             """},
#             {"role": "system", "content":"""
#             요소 출력 시 규칙은 다음과 같습니다.
            
#             keyword1,연결강도1/keyword2,연결 강도/keyword3,연결 강도/
            
#             # 중요: 위와 같은 출력 규칙을 반드시 지키세요. 코드로 자동화할 것이기에 규칙이 반드시 지켜져야 합니다.
#             # 중요: 키워드에는 다음과 같은 단어를 포함하지 마세요. 기관명을 나타내기 때문에 유의미한 정보가 아닙니다. (제외 목록: 3GPP, ETSI, TSG, WG*, TCCA)
#                 - 해당 정보는 본인이 판단하기에 국가명, 단체명과 같이 유의미하지 않다면 포함하지 마세요.
#             # 중요: 연결 강도는 integer로서 해당 keyword가 표현할 수 있는 뉴스의 정도를 나타냅니다. 즉, 중요한 키워드일 수록 값이 높습니다. 연결 강도는 추후 추천 시스템에서 활용되기에 점수 간의 격차가 어느 정도 있도록 정하세요.
#             """},
#             {"role": "system", "content": "키워드는 영어로 구성하세요."},
#             {"role": 'user', "content": user_msg}
#         ]

#         return msg

#     def use_chat_gpt_for_extraction(self, content):
#         message = self.make_message(f"Content: {content}")

#         chat_response = self.chat_completion_request(message)

#         return chat_response.choices[0].message.content

# from keybert import KeyBERT
# from sentence_transformers import SentenceTransformer


# class Extractor:
#     def __init__(self):
#         self.model = SentenceTransformer('allenai/scibert_scivocab_uncased')
#         self.kw_model = KeyBERT(model = self.model)

#     def extract_keywords(self, content):
#         keywords = self.kw_model.extract_keywords(content, keyphrase_ngram_range=(1, 2), top_n=5)

#         print("[Extract_keywords.py] Result of extraction")
#         print(keywords)

#         return keywords


from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Extractor:
    def __init__(self, model_name="allenai/scibert_scivocab_uncased"):
        """
        KeywordRelevance 클래스 초기화
        :param keywords: 키워드 리스트
        :param model_name: 임베딩 모델 이름
        """
        self.keywords = [
            "Resource/RAN Slicing", "Quality of Service", "Latency", "URLLC", "eMBB", "5G", "5G Core", 
            "Edge computing", "Handover", "VoLTE", "VoNR", "SIP", "Beamforming", "Massive MIMO",
            "Dynamic Spectrum Sharing (DSS)", "Small cells", "Audio codec", "VR/AR streaming", "Real-time encoding", "RF calibration",
            "UE capabilities", "Dual connectivity", "Load balancing", "Interface testing",
            "Signaling protocols", "Authentication", "Security", "Fault tolerance", "Internet of Things (IoT)",
            "Compliance testing", "Performance testing", "Sub-6 GHz", "mmWave", "Carrier Aggregation",
            "Ultra-low latency", "Private",  "Media optimization", "Adaptive streaming", "Spectrum efficiency", "Interference management", 
            "Mobility Management", "Test equipment", "Access Network", "Bandwidth",
            "Core Network", "Evolved Packet Core (EPC)", "Heterogeneous", "Spectrum efficiency", "Machine Type Communication (MTC)", 
            "Function Virtualization (NFV)", "Orthogonal Frequency Division Multiplexing (OFDM)", "Packet Data Convergence Protocol (PDCP)",
            "Quality of Experience (QoE)", "Radio Resource Control (RRC)", "Non-Terrestrial Netowkr (NTN)",
            "Subscriber Identity Module (SIM)", "Time Division Duplex (TDD)", "User Equipment (UE)",
            "Wireless Local Area Network (WLAN)", "Enhanced Mobile Broadband (eMBB)", "Unmanned-Aireal Vehicle", "Vehicle communications (V2X, V2V)",
            "Self-Organizing Networks (SON)", "Licensed Assisted Access (LAA)", 
            "Artificial Intelligence (AI)", "Machine Learning (ML)", "Cloud RAN (C-RAN)", "Open RAN (O-RAN)",
            "Network Automation", "Software-Defined Networking (SDN)", "6G"
        ]
        self.model = SentenceTransformer(model_name)
        self.keyword_embeddings = self.model.encode(self.keywords)
    
    def extract_keywords(self, news_content, top_n=5):
        """
        뉴스 콘텐츠를 입력받아 키워드 관련도를 계산
        :param news_content: 뉴스 콘텐츠 (문자열)
        :param top_n: 상위 N개의 관련 키워드 반환
        :return: [(keyword1, value1), (keyword2, value2), ...]
        """
        # 뉴스 콘텐츠 임베딩 계산
        news_embedding = self.model.encode(news_content)
        
        # 코사인 유사도 계산
        similarities = cosine_similarity([news_embedding], self.keyword_embeddings)[0]
        
        # 관련도 높은 순으로 정렬
        sorted_indices = np.argsort(similarities)[::-1]
        top_keywords = [(self.keywords[i], similarities[i]) for i in sorted_indices[:top_n]]

        print("[Extract_keywords.py] Result of extraction")
        print(top_keywords)

        return top_keywords
