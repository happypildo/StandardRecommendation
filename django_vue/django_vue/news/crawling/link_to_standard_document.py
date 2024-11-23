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

class StringToWordConnection:
    def __init__(self, series_num, keywords, weights, model_name="bert-base-uncased"):
        print(f"Loading model '{model_name}'...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        print("Model loaded successfully!")

        self.string = series_descriptions[series_num]
        self.series_num = series_num
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

    def visualize_graph(self, scores, threshold=0.1):
        """
        Visualizes the graph with node sizes and colors based on edge weights.
        Applies gradient coloring to nodes and includes a colorbar.

        :param scores: Similarity scores between the string and keywords.
        :param threshold: Minimum connection strength to display an edge.
        """
        G = nx.Graph()

        # Add nodes
        G.add_node(self.string, color="red")  # Main string node
        G.add_nodes_from(self.keywords, color="blue")  # Keywords

        # Add edges with weights
        for i, keyword in enumerate(self.keywords):
            if scores[i] >= threshold:
                G.add_edge(self.string, keyword, weight=scores[i])

        # Calculate node weights (sum of edge weights)
        node_weights = {}
        for node in G.nodes:
            node_weights[node] = sum([data["weight"] for _, _, data in G.edges(node, data=True)])

        # Normalize weights for visualization (0 to 1)
        max_weight = max(node_weights.values()) if node_weights else 1
        normalized_weights = {node: weight / max_weight for node, weight in node_weights.items()}

        # Generate colors using a colormap
        cmap = cm.get_cmap('coolwarm')  # You can try other colormaps like 'viridis', 'plasma', etc.
        node_colors = [cmap(normalized_weights[node]) for node in G.nodes]

        # Calculate node sizes
        node_sizes = [300 + normalized_weights[node] * 1000 for node in G.nodes]
        font_sizes = [10 + (node_weights[node] / max_weight) * 20 for node in G.nodes]

        # Draw graph
        fig, ax = plt.subplots(constrained_layout=True)
        pos = nx.spring_layout(G)  # Circular layout for the graph
        nx.draw(
            G, pos, node_color=node_colors, node_size=node_sizes, edge_color="gray", font_size=10
        )

        # Draw edge weights
        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.2f}" for k, v in edge_labels.items()})
        specific_labels = {
            key: value for key, value in zip(self.keywords, self.keywords)
        }
        specific_labels[self.string] = f"Series: {self.series_num}"
        # nx.draw_networkx_labels(G, pos, )

        for i, (node, (x, y)) in enumerate(pos.items()):
            plt.text(
                x,
                y,
                s=specific_labels[node],
                fontsize=font_sizes[i],
                ha="center",
                va="center",
            )

        # Add colorbar for gradient scale
        sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_weight))
        sm.set_array([])  # Required to link ScalarMappable to the colorbar
        fig.colorbar(sm, label="Node Weight (Gradient Scale)", ax=plt.gca())  # Attach colorbar to current Axes

        # Get current size and calculate new height
        current_width, current_height = fig.get_size_inches()
        new_width = 20  # Desired width
        new_height = (new_width / current_width) * current_height  # Adjust height to maintain aspect ratio

        # Set new size
        fig.set_size_inches(new_width, new_height)
        # plt.show()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return image_base64

    def process(self, threshold=0.1):
        """
        Processes the string and keywords to visualize their connection graph.

        :param string: Input string.
        :param keywords: List of keywords.
        :param threshold: Minimum connection strength to display an edge.
        """
        print("Calculating similarity...")
        scores = self.calculate_similarity()

        print("Visualizing connection graph...")
        return self.visualize_graph(scores, threshold)

    def get_network_data(self):
        string_embedding = self.get_embedding(self.string)
        keyword_embeddings = [self.get_embedding(keyword) for keyword in self.keywords]

        similarities = []
        for idx, keyword_embedding in enumerate(keyword_embeddings):
            similarity = np.dot(string_embedding, keyword_embedding) / (
                np.linalg.norm(string_embedding) * np.linalg.norm(keyword_embedding) + 1e-9
            )
            similarities.append(similarity * self.weights[idx])

        nodes = []
        for k in self.keywords:
            nodes.append({
                "id": k, "group": 1
            })
        nodes.append({
            "id": f"Series: {self.series_num}"
        })

        links = []
        for idx, k in enumerate(self.keywords):
            links.append({
                'source': k,
                'target': f"Series: {self.series_num}",
                "weight": similarities[idx].item()
            })
        
        return {"nodes": nodes, "links": links}


# # Example usage
# # Instantiate the class with a pre-trained transformer model
# stwc = StringToWordConnection(
#     release_num=18,
#     keywords=["AI", "Machine Learning", "Data Science", "Innovation", "Nonterrestrial-Netowrk"],
#     weights=[5, 2, 1, 0.5, 0.7],
#     model_name="bert-base-uncased"
# )

# # Process and visualize
# stwc.process(threshold=0.1)
