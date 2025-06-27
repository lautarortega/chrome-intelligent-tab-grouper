import json

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from typing import List, Dict
import re
from urllib.parse import urlparse


class TabGroupingInference:
    """
    Class for performing intelligent tab grouping inference using text embeddings and clustering.
    Groups browser tabs based on URL and title similarity.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', min_cluster_size: int = 2, eps: float = 0.3,):
        """
        Initializes the inference model.

        Args:
            model_name: Name of the SentenceTransformer model to use
            min_cluster_size: Minimum size to consider a cluster as meaningful
        """
        self.model = SentenceTransformer(model_name)
        self.min_cluster_size = min_cluster_size
        self.eps = eps

    def preprocess_text(self, url: str, title: str) -> str:
        """
        Preprocesses URL and title to create cleaner text for embeddings.

        Args:
            "url": Tab URL
            "title": Tab title

        Returns:
            Combined and processed text
        """
        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.hostname.lower()

        # Clean title (remove excessive special characters)
        clean_title = re.sub(r'[^\w\s-]', ' ', title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        # Extract path keywords from URL
        path_keywords = []
        if parsed_url.path:
            path_parts = [part for part in parsed_url.path.split('/') if part and len(part) > 2]
            path_keywords = path_parts[:3]  # Take only the first 3 most relevant parts

        # Combine relevant information
        combined_text = f"{clean_title} {domain} {' '.join(path_keywords)}"
        return combined_text.lower()

    def create_embeddings(self, tabs_data: dict) -> np.ndarray:
        """
        Creates embeddings for all tabs.

        Args:
            tabs_data: List of dictionaries with 'url' and 'title' for each tab

        Returns:
            Numpy array with embeddings for each tab
        """
        processed_texts = []

        for tab in tabs_data.values():
            processed_text = self.preprocess_text(tab['url'], tab['title'])
            processed_texts.append(processed_text)

        # Create embeddings using SentenceTransformer
        embeddings = self.model.encode(processed_texts, convert_to_tensor=False)
        return embeddings

    # def find_optimal_clustering_params(self, embeddings: np.ndarray) -> float:
    #     """
    #     Finds optimal parameters for DBSCAN based on data distribution.
    #
    #     Args:
    #         embeddings: Tab embeddings
    #
    #     Returns:
    #         eps: Epsilon parameter for DBSCAN clustering
    #     """
    #     if len(embeddings) < 3:
    #         return 0.3
    #
    #     # Normalize embeddings
    #     norm_embeddings = normalize(embeddings)
    #
    #     # Calculate cosine similarity matrix
    #     similarity_matrix = cosine_similarity(norm_embeddings)
    #
    #     # Convert similarity to distance
    #     distance_matrix = 1 - similarity_matrix
    #
    #     # Find average distances excluding diagonal
    #     distances = []
    #     for i in range(len(distance_matrix)):
    #         for j in range(i + 1, len(distance_matrix)):
    #             distances.append(distance_matrix[i][j])
    #
    #     distances = np.array(distances)
    #
    #     # Use percentile to determine eps
    #     eps = np.percentile(distances, x :=10)  # Take x% of smallest distances
    #     print("10 percentile distance:", np.percentile(distances, x :=10), "\n")
    #     print("20 percentile distance:", np.percentile(distances, x :=20), "\n")
    #     print("30 percentile distance:", np.percentile(distances, x :=30), "\n")
    #     return eps

    def perform_clustering(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Performs clustering using DBSCAN with optimized parameters.

        Args:
            embeddings: Tab embeddings

        Returns:
            Array with cluster labels for each tab
        """
        if len(embeddings) < 2:
            return np.array([0] * len(embeddings))

        # eps = self.find_optimal_clustering_params(embeddings)

        # Use cosine distance for clustering
        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_cluster_size,
            metric='cosine'
        )

        cluster_labels = clustering.fit_predict(embeddings)
        return cluster_labels

    def filter_meaningful_clusters(self, cluster_labels: np.ndarray,
                                   tabs_data: dict) -> Dict[int, List[int]]:
        """
        Filters clusters to keep only meaningful ones.

        Args:
            cluster_labels: Cluster labels
            tabs_data: Original tab data

        Returns:
            Dictionary with cluster_id -> list of tab indices
        """
        meaningful_clusters = {}

        # Group tabs by cluster
        for tab_idx, cluster_id in zip(tabs_data.keys(), cluster_labels):
            if cluster_id == -1:  # Noise in DBSCAN
                continue
            cluster_id = str(cluster_id)
            if cluster_id not in meaningful_clusters:
                meaningful_clusters[cluster_id] = {}
            meaningful_clusters[cluster_id].update({tab_idx: tabs_data[tab_idx]})

        # Filter clusters that do not form a group (at least two tabs)
        filtered_clusters = {
            cluster_id: tab_indices
            for cluster_id, tab_indices in meaningful_clusters.items()
            if len(tab_indices) >= self.min_cluster_size
        }

        return filtered_clusters

    def inference(self, tabs_data: dict) -> Dict[str, any]:
        """
        Main inference function for tab grouping.

        Args:
            tabs_data: List of dictionaries with 'url' and 'title' for each tab

        Returns:
            Dictionary with grouping results
        """
        if not tabs_data or len(tabs_data) < 2:
            return {
                'clusters': {},
                'unclustered_tabs': [key for key in tabs_data.keys()],
                'total_tabs': len(tabs_data),
                'num_clusters': 0
            }

        # Create embeddings
        embeddings = self.create_embeddings(tabs_data)

        # Perform clustering
        cluster_labels = self.perform_clustering(embeddings)

        # Filter meaningful clusters
        meaningful_clusters = self.filter_meaningful_clusters(cluster_labels, tabs_data)

        # Identify ungrouped tabs
        clustered_tab_indices = set()
        for tabs in meaningful_clusters.values():
            clustered_tab_indices.update(tabs.keys())

        unclustered_tabs = [
            tab_id for tab_id in tabs_data.keys()
            if tab_id not in clustered_tab_indices
        ]

        return {
            'clusters': meaningful_clusters,
            'unclustered_tabs': unclustered_tabs,
            'total_tabs': len(tabs_data),
            'num_clusters': len(meaningful_clusters)
        }

    def get_cluster_summary(self, cluster_tab_indices: List[int],
                            tabs_data: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Generates a descriptive summary of a cluster.

        Args:
            cluster_tab_indices: Tab indices in the cluster
            tabs_data: Original tab data

        Returns:
            Dictionary with cluster information
        """
        if not cluster_tab_indices:
            return {'name': 'Empty Cluster', 'description': ''}

        # Extract domains and titles
        domains = []
        titles = []

        for idx in cluster_tab_indices:
            tab = tabs_data[idx]
            domain = urlparse(tab['url']).netloc.lower()
            domains.append(domain)
            titles.append(tab['title'])

        # Find most common domain
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        most_common_domain = max(domain_counts.items(), key=lambda x: x[1])[0]

        # Generate cluster name
        if domain_counts[most_common_domain] == len(cluster_tab_indices):
            cluster_name = f"Group of {most_common_domain}"
        else:
            cluster_name = f"Mixed group ({len(cluster_tab_indices)} tabs)"

        return {
            'name': cluster_name,
            'description': f"Cluster with {len(cluster_tab_indices)} tabs",
            'dominant_domain': most_common_domain,
            'tab_count': len(cluster_tab_indices)
        }


# Convenience function for direct use
def group_tabs(tabs_data,
               model_name: str = 'all-MiniLM-L6-v2',
               min_cluster_size: int = 2,
               eps: float = 0.3) -> Dict[str, any]:
    """
    Convenience function to group tabs directly.

    Args:
        tabs_data: List of dictionaries with 'id', 'url' and 'title'
        model_name: SentenceTransformer model to use
        min_cluster_size: Minimum meaningful cluster size

    Returns:
        Grouping results
    """
    inference_engine = TabGroupingInference(model_name, min_cluster_size, eps)
    return inference_engine.inference(tabs_data)


# Example usage
if __name__ == "__main__":
    # Example data
    with open("sample_data/tab_grouper.json", 'r') as file:
        sample_tabs = json.load(file)

    # Create groups
    for epsilon in np.linspace(0.25, 0.6, 5):
        epsilon = 0.5
        results = group_tabs(sample_tabs, eps=epsilon)

        print(f"Epsilon: {epsilon}")
        print(f"Total tabs: {results['total_tabs']}")
        print(f"Clusters found: {results['num_clusters']}")
        print(f"Unclustered tabs: {len(results['unclustered_tabs'])}")

        for cluster_id, tab_indices in results['clusters'].items():
            print(f"\nCluster {cluster_id}:")
            for idx in tab_indices:
                tab = sample_tabs[idx]
                print(f"  - {tab['title']} ({tab['url']})")
        break

# todo: enhance preprocessing