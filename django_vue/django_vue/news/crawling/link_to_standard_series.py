series_descriptions = {
    1: "This series outlines the general aspects and fundamental principles of the GSM system, including its technical architecture, operational scenarios, and core functionalities for mobile communication networks.",
    2: "Service-related aspects of the GSM system, detailing how user-centric services such as voice, SMS, and supplementary services are designed, implemented, and managed in a mobile network environment.",
    3: "Explores the network architecture and design principles of the GSM system, including the structural organization of Base Stations, Mobile Switching Centers, and other network elements.",
    4: "Focuses on the MS-BSS interface, including the specifications for communication protocols and signaling procedures between mobile stations and base station subsystems in GSM networks.",
    5: "Describes the physical layer of the GSM system, particularly focusing on the radio path characteristics, modulation techniques, and physical channel structures used for efficient data transmission.",
    6: "Specifications for speech codec technologies used in GSM systems to compress voice signals while maintaining high audio quality over limited bandwidth.",
    7: "Defines the terminal adaptor interface allowing GSM mobile stations to connect and communicate with public data networks for data transmission and access services.",
    8: "Details the BSS-MSC interface and the communication protocols that manage handover, signaling, and traffic between the Base Station Subsystem and the Mobile Switching Center.",
    9: "Explains the interworking mechanisms between GSM and other telecommunication networks, such as PSTN, ISDN, and emerging packet-switched networks, for seamless service integration.",
    10: "Describes connection types within the GSM Public Land Mobile Network (PLMN), including configurations for roaming, handover, and interconnection with other networks.",
    11: "Provides equipment and type approval specifications to ensure interoperability and compliance with GSM standards across different devices and vendors.",
    12: "Covers the operation and maintenance procedures of GSM networks, including network monitoring, fault management, and performance optimization techniques.",
    13: "Focuses on the security-related functions of GSM networks, such as encryption, authentication, and secure key management protocols to protect user data and prevent fraud.",
    14: "Details enhancements made to the GSM system, including new features, improved performance capabilities, and backward-compatible upgrades to existing infrastructure.",
    15: "Describes data communication services in GSM, including circuit-switched data and General Packet Radio Service (GPRS) for internet access and multimedia messaging.",
    16: "Focuses on the features and technical capabilities of GSM mobile stations, including hardware specifications, software capabilities, and compatibility with network services.",
    17: "Explores the features provided by the GSM network, such as location-based services, call forwarding, and intelligent network functionalities.",
    18: "Details the radio aspects of GSM, including frequency allocation, signal propagation characteristics, and interference management techniques.",
    19: "Describes the processes and technologies for speech processing in GSM, including echo cancellation, voice activity detection, and error correction.",
    20: "Focuses on data transmission methodologies in GSM, including techniques for reliable delivery, compression, and error detection across the mobile network.",
    21: "Provides comprehensive specifications for GSM signaling protocols used for communication between network entities, such as SS7 and LAPD protocols.",
    22: "Defines service requirements for UMTS systems, focusing on user expectations, service availability, and quality-of-service parameters in 3G networks.",
    23: "Covers the technical realization of UMTS service aspects, including implementation frameworks, system design, and integration with legacy networks.",
    24: "Describes signaling protocols and switching mechanisms in UMTS systems for efficient resource allocation and session management.",
    25: "Focuses on Radio Access Network (RAN) aspects in UMTS, including specifications for Node B, RNC, and their interaction with the core network.",
    26: "Explores codec technologies and multimedia services in UMTS, enabling advanced applications such as video streaming and interactive gaming.",
    27: "Covers data services and terminal interfaces in UMTS, detailing protocols for internet connectivity, multimedia messaging, and device interconnectivity.",
    28: "Provides extended specifications for signaling protocols and switching techniques, ensuring scalability and robustness in UMTS systems.",
    29: "Focuses on core network protocols in UMTS, detailing communication standards between core components such as HLR, MSC, and SGSN.",
    30: "Describes charging and billing mechanisms in UMTS, including techniques for usage metering, billing accuracy, and fraud prevention.",
    31: "Provides additional specifications for security-related network functions in UMTS, ensuring data integrity and user privacy.",
    32: "Focuses on telecommunication management, including charging management and the integration of management systems across network domains.",
    33: "Explores security aspects in UMTS, focusing on encryption algorithms, authentication procedures, and secure communication frameworks.",
    34: "Defines test specifications for UMTS, including compliance testing, performance benchmarking, and interoperability validation.",
    35: "Details security algorithms used in UMTS, including cryptographic methods for encryption, integrity checking, and secure key distribution.",
    36: "Describes Evolved Universal Terrestrial Radio Access (E-UTRA), commonly known as LTE, focusing on advanced features, high-speed data transmission, and reduced latency.",
    37: "Explores radio measurement and protocol aspects in LTE, including channel quality indicators, feedback mechanisms, and link adaptation techniques.",
    38: "Focuses on NR (New Radio) technology in 5G, detailing its capabilities, advanced modulation techniques, and support for massive IoT and low-latency applications.",
    39: "Describes interworking mechanisms between 3GPP and non-3GPP systems, ensuring seamless user experience across heterogeneous networks.",
    40: "Focuses on service aspects in 3GPP systems, including the evolution of user services and the integration of advanced functionalities in Stage 2 development.",
    41: "Outlines the general principles and architectural aspects of 3GPP systems, including foundational concepts and long-term evolution strategies.",
    42: "Explores service-related aspects in 3GPP systems, focusing on user-centric service enhancements and operational efficiency.",
    43: "Details network architecture and design aspects of 3GPP systems, including core network evolution and RAN optimization techniques.",
    44: "Focuses on MS-BSS interface specifications in 3GPP, ensuring interoperability and performance across diverse network configurations.",
    45: "Describes physical layer aspects on the radio path in 3GPP systems, including modulation, channel coding, and resource allocation strategies.",
    46: "Provides specifications for speech codecs in 3GPP systems, ensuring high-quality voice communication over limited bandwidth.",
    47: "Details terminal adaptor features in 3GPP systems, enabling seamless integration with public data networks and enterprise solutions.",
    48: "Covers BSS-MSC interface specifications in 3GPP, ensuring robust signaling and traffic management in advanced networks.",
    49: "Explores interworking techniques between 3GPP and other network standards, enabling global connectivity and seamless roaming."
}

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


