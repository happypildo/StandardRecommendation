import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors


class KeywordConnection:
    def __init__(self, word2vec_model_path=None):
        """
        Initializes the KeywordConnection class.

        :param word2vec_model_path: Path to a pre-trained Word2Vec model.
        """
        if word2vec_model_path:
            print("Loading pre-trained Word2Vec model...")
            self.model = KeyedVectors.load_word2vec_format(word2vec_model_path, binary=True)
        else:
            self.model = None

    def train_word2vec(self, sentences):
        """
        Trains a Word2Vec model on the provided sentences.

        :param sentences: List of tokenized sentences for training.
        """
        print("Training Word2Vec model...")
        self.model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4).wv

    def get_vector(self, word):
        """
        Fetches the vector for a given word using the Word2Vec model.

        :param word: Word to fetch the vector for.
        :return: Word vector.
        """
        if word in self.model:
            return self.model[word]
        else:
            print(f"Word '{word}' not found in vocabulary. Using zero vector.")
            return np.zeros(self.model.vector_size)

    def calculate_similarity(self, keywords_a, keywords_b):
        """
        Calculates the cosine similarity between keywords from A and B.

        :param keywords_a: List of keywords from A.
        :param keywords_b: List of keywords from B.
        :return: Similarity matrix.
        """
        vectors_a = np.array([self.get_vector(word) for word in keywords_a])
        vectors_b = np.array([self.get_vector(word) for word in keywords_b])

        norm_a = np.linalg.norm(vectors_a, axis=1, keepdims=True)
        norm_b = np.linalg.norm(vectors_b, axis=1, keepdims=True)
        similarity_matrix = np.dot(vectors_a, vectors_b.T) / (norm_a * norm_b.T + 1e-9)
        return similarity_matrix

    def build_connection_matrix(self, similarity_matrix, scores_b):
        """
        Builds a connection matrix by weighting similarity values with B's scores.

        :param similarity_matrix: Cosine similarity matrix.
        :param scores_b: List of scores for B's keywords.
        :return: Weighted connection matrix.
        """
        return similarity_matrix * np.array(scores_b)

    def visualize_graph(self, keywords_a, keywords_b, connection_matrix, threshold=0.1):
        """
        Visualizes the connection graph using NetworkX and Matplotlib.

        :param keywords_a: List of keywords from A.
        :param keywords_b: List of keywords from B.
        :param connection_matrix: Weighted connection matrix.
        :param threshold: Minimum connection strength to display an edge.
        """
        G = nx.Graph()

        # Add nodes
        G.add_nodes_from(keywords_a, bipartite=0)
        G.add_nodes_from(keywords_b, bipartite=1)

        # Add edges
        for i, a in enumerate(keywords_a):
            for j, b in enumerate(keywords_b):
                weight = connection_matrix[i][j]
                if weight >= threshold:
                    G.add_edge(a, b, weight=weight)

        # Draw graph
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", font_size=10)
        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.2f}" for k, v in edge_labels.items()})
        plt.show()

    def process(self, keywords_a, keywords_b, scores_b, threshold=0.1):
        """
        Processes the keywords and visualizes the connection graph.

        :param keywords_a: List of keywords from A.
        :param keywords_b: List of keywords from B.
        :param scores_b: List of scores for B's keywords.
        :param threshold: Minimum connection strength to display an edge.
        """
        print("Calculating similarity matrix...")
        similarity_matrix = self.calculate_similarity(keywords_a, keywords_b)

        print("Building connection matrix...")
        connection_matrix = self.build_connection_matrix(similarity_matrix, scores_b)

        print("Visualizing connection graph...")
        self.visualize_graph(keywords_a, keywords_b, connection_matrix, threshold)


# Example usage
# Pre-trained Word2Vec model path (optional)
word2vec_model_path = "path/to/pretrained/word2vec/model.bin"  # Optional: Use pre-trained model
kc = KeywordConnection()

# Example sentences for training Word2Vec (if no pre-trained model is used)
sentences = [
    ["AI", "is", "transforming", "technology"],
    ["Machine", "Learning", "is", "a", "subset", "of", "AI"],
    ["Data", "Science", "involves", "analyzing", "data"]
]
kc.train_word2vec(sentences)

# Keywords and scores
keywords_a = ["AI", "Machine Learning", "Data Science"]
keywords_b = ["AI", "Deep Learning", "Big Data"]
scores_b = [0.9, 0.7, 0.5]

# Process and visualize
kc.process(keywords_a, keywords_b, scores_b)
