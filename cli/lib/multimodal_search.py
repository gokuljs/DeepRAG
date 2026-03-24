import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

from .search_utils import load_movies


class MultimodalSearch:
    """Multimodal search using CLIP to embed images and text into a shared vector space."""

    def __init__(self, model_name="clip-ViT-B-32", documents=None):
        self.model = SentenceTransformer(model_name)
        self.documents = documents or []

        if self.documents:
            self.texts = [
                f"{doc['title']}: {doc['description']}" for doc in self.documents
            ]
            self.text_embeddings = self.model.encode(self.texts, show_progress_bar=True)

    def embed_image(self, image_path):
        image = Image.open(image_path)
        return self.model.encode([image])[0]

    def search_with_image(self, image_path):
        image_embedding = self.embed_image(image_path)

        results = []
        for i, text_emb in enumerate(self.text_embeddings):
            similarity = cosine_similarity(image_embedding, text_emb)
            results.append({
                "id": self.documents[i]["id"],
                "title": self.documents[i]["title"],
                "description": self.documents[i]["description"],
                "similarity": similarity,
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:5]


def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


def verify_image_embedding(image_fpath):
    ms = MultimodalSearch()
    embedding = ms.embed_image(image_fpath)
    print(f"Embedding shape: {embedding.shape[0]} dimensions")


def image_search_command(image_path):
    documents = load_movies()
    ms = MultimodalSearch(documents=documents)
    return ms.search_with_image(image_path)
