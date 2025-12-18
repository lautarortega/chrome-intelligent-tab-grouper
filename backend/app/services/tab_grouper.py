import re
import logging
from urllib.parse import urlparse
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from typing import List, Dict, Any
from app.schemas.tabs import Tab
from app.core.config import settings

logger = logging.getLogger(__name__)

class TabGrouperService:
    def __init__(self, model_name: str = settings.MODEL_NAME, 
                 min_cluster_size: int = settings.MIN_CLUSTER_SIZE, 
                 eps: float = settings.DBSCAN_EPS):
        logger.info(f"Initializing TabGrouperService with model: {model_name}, eps: {eps}")
        self.model = SentenceTransformer(model_name)
        self.min_cluster_size = min_cluster_size
        self.eps = eps

    def preprocess_text(self, url: str, title: str) -> str:
        parsed_url = urlparse(url)
        domain = parsed_url.hostname.lower() if parsed_url.hostname else ""

        clean_title = re.sub(r'[^\w\s-]', ' ', title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        path_keywords = []
        if parsed_url.path:
            path_parts = [part for part in parsed_url.path.split('/') if part and len(part) > 2]
            path_keywords = path_parts[:3]

        combined_text = f"{clean_title} {domain} {' '.join(path_keywords)}"
        return combined_text.lower()

    def create_embeddings(self, tabs: List[Tab]) -> np.ndarray:
        processed_texts = [self.preprocess_text(tab.url, tab.title) for tab in tabs]
        logger.debug(f"Encoding {len(processed_texts)} texts")
        return self.model.encode(processed_texts, convert_to_tensor=False)

    def group_tabs(self, tabs: List[Tab]) -> Dict[str, Any]:
        logger.info(f"Grouping {len(tabs)} tabs")
        if not tabs or len(tabs) < 2:
            logger.info("Not enough tabs to group")
            return {
                'clusters': {},
                'unclustered_tabs': tabs,
                'total_tabs': len(tabs),
                'num_clusters': 0
            }

        embeddings = self.create_embeddings(tabs)
        
        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_cluster_size,
            metric='cosine'
        )
        cluster_labels = clustering.fit_predict(embeddings)

        clusters = {}
        unclustered_tabs = []

        for tab, label in zip(tabs, cluster_labels):
            if label == -1:
                unclustered_tabs.append(tab)
            else:
                label_str = str(label)
                if label_str not in clusters:
                    clusters[label_str] = []
                clusters[label_str].append(tab)
        
        # Filter clusters that don't meet min_cluster_size
        final_clusters = {}
        for label, cluster_tabs in clusters.items():
            if len(cluster_tabs) >= self.min_cluster_size:
                final_clusters[label] = cluster_tabs
            else:
                unclustered_tabs.extend(cluster_tabs)

        logger.info(f"Found {len(final_clusters)} clusters, {len(unclustered_tabs)} unclustered tabs")
        return {
            'clusters': final_clusters,
            'unclustered_tabs': unclustered_tabs,
            'total_tabs': len(tabs),
            'num_clusters': len(final_clusters)
        }
