import json
import os

import fitz
import re

import glob

from pprint import pprint
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Extractor:
    def __init__(self, target_path=""):
        self.extracted_data = []
        self.target_path = target_path
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
        self.model = SentenceTransformer("pritamdeka/S-BioBert-snli-multinli-stsb")
        self.keyword_embeddings = self.model.encode(self.keywords)


    def is_valid_title(self, str):
        # 정규 표현식 패턴 정의
        pattern = r"V\d+\.\d+\.\d+"
        
        # 패턴 매칭
        match = re.search(pattern, str)
        
        # 패턴이 있으면 True, 없으면 False 반환
        return match is not None

    def extract_content_from_pdf(self):
        pdf_files = glob.glob(f"{self.target_path}/*.pdf")
        extracted_data = []
        for filename in pdf_files:
            file_path = os.path.abspath(f"./{filename}")

            pdf = fitz.open(file_path)
            all_text = ""
            for page_num in range(len(pdf)):
                page = pdf[page_num]  # 현재 페이지 가져오기
                text = page.get_text()  # 페이지에서 텍스트 추출
                all_text += text  # 텍스트를 누적
                all_text += "\n"  # 페이지 구분을 위해 줄바꿈 추가
            
            pdf.close()
            try:
                sp_text = all_text.split("\n")
                title = sp_text[0].replace("\n", " ")
                
                if not self.is_valid_title(title):
                    continue

                area_s = all_text.index('Technical Report')
                area_e = all_text.index('The present document has been developed within the 3rd Generation Partnership Project')
                area = all_text[area_s:area_e]
                area_s = area.index('3rd Generation Partnership Project')
                area = area[area_s + len('3rd Generation Partnership Project'):]
                area = area.replace("\n", " ")

                if area.strip() == "":
                    continue

                print(title, area)
                
                pattern = r"(?<=\n)[\w\s]+(?=\.{5,})"
                matches = re.findall(pattern, all_text)

                start_idx = 0
                for match in matches:
                    if 'Abbreviations' in match:
                        break
                    start_idx += 1
                all_indices = matches[start_idx+1:]

                processed_indices = []
                for idx, match in enumerate(all_indices):
                    spl_match = match.split("\n")
                    for spl in spl_match:
                        temp = spl.strip()
                        if temp.isdigit():
                            pass
                        else:
                            temp = temp.replace("3GPP", "")
                            temp = temp.replace("TR", "")
                            temp = temp.replace("TS", "")
                            
                            if temp.strip() == "":
                                continue
                            processed_indices.append(temp)
                processed_indices = set(processed_indices)
                if len(processed_indices) == 0:
                    continue

                print()
                print(", ".join(processed_indices))
                

                indices_embedding = self.model.encode(", ".join(processed_indices))
                similarities = cosine_similarity([indices_embedding], self.keyword_embeddings)[0]

                # 관련도 높은 순으로 정렬
                sorted_indices = np.argsort(similarities)[::-1]
                # top_keywords = [(self.keywords[i], similarities[i]) for i in sorted_indices[:5]]
                top_keywords = [f"{self.keywords[i]} with similarity {similarities[i]}" for i in sorted_indices[:5]]
                top_keywords = ", ".join(top_keywords)
                print("-"*30)
                print(top_keywords)
                print("-"*30)
                # top_keywords_str = ""
                # try:
                #     for k, _ in top_keywords:
                #         print(k)
                #         top_keywords += k + ", "
                # except:
                #     pass
                # print()

                extracted_data.append({
                    "title": title,
                    "area": area,
                    "indices": ", ".join(processed_indices),
                    "keywords":  top_keywords
                })
                pprint(extracted_data[-1])
            except Exception as e:
                print(e)
                pass
        
        return extracted_data
