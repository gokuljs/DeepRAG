import re
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
from .search_utils import load_movies

CACHE_PATH = Path(__file__).resolve().parents[1] / "cache"
CACHE_PATH.mkdir(parents=True, exist_ok=True)


class SemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings_path = CACHE_PATH / "embeddings.npy"
        self.embeddings = None
        self.documents = []
        self.document_map = {}

    def build_embeddings(self, documents):
        """
        Build embeddings for a given list of documents.
        """
        self.documents = documents
        self.document_map = {}
        movie_strings = []
        for movie in self.documents:
            self.document_map[movie["id"]] = movie
            movie_strings.append(f"{movie['title']} {movie['description']}")
        self.embeddings = self.model.encode(movie_strings)
        np.save(self.embeddings_path, self.embeddings)
        return self.embeddings

    def load_and_create_embeddings(self, documents):
        """
        Load embeddings from cache and create embeddings for a given list of documents.
        """
        self.documents = documents
        self.document_map = {}
        for doc in self.documents:
            self.document_map[doc["id"]] = doc
        if self.embeddings_path.exists():
            self.embeddings = np.load(self.embeddings_path)
            if len(self.embeddings) == len(self.documents):
                return self.embeddings
        return self.build_embeddings(self.documents)

    def generate_embeddings(self, text: str):
        """
        Generate embeddings for a given text.
        """
        if text is None or text.strip() == "":
            raise ValueError("Text cannot be None or empty")
        return self.model.encode([text])[0]

    def search(self, query: str, n_results: int = 10):
        """
        Search for the most similar documents to a given query.
        """
        if self.embeddings is None:
            raise ValueError("Embeddings are not loaded")
        query_embedding = self.generate_embeddings(query)
        similarities = []
        for doce_emb, doc in zip(self.embeddings, self.documents):
            similarity = cosine_similarity(query_embedding, doce_emb)
            similarities.append((similarity, doc))
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [
            {"score": sc, "title": doc["title"], "description": doc["description"]}
            for sc, doc in similarities[:n_results]
        ]


def verify_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Verify the model is loaded correctly.
    """
    model = SentenceTransformer(model_name)
    print(f"Model loaded: {model}")
    print(f"Max sequence length: {model.max_seq_length}")


def embed_text(text: str):
    """
    Embed a given text.
    """
    return SemanticSearch().generate_embeddings(text)


def verify_embeddings():
    ss = SemanticSearch()
    documents = load_movies()
    embeddings = ss.load_and_create_embeddings(documents)
    print("length of the documents: ", len(documents))
    print("embedding shape: ", embeddings.shape[0])


def embed_query_text(query):
    """
    Embed a given query text.
    """
    ss = SemanticSearch()
    result = ss.generate_embeddings(query)
    print(query)
    print("embedding shape: ", result.shape)
    print("embedding: ", result)


def cosine_similarity(vec1, vec2):
    """
    Calculate the cosine similarity between two vectors.
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)

def search_command(query, n_results=5):
    """
    Search for the most similar documents to a given query.
    """
    ss = SemanticSearch()
    documents = load_movies()
    ss.load_and_create_embeddings(documents)
    results = ss.search(query, n_results)
    for i,result in enumerate(results):
        print(f"{i + 1}. {result['title']} \n {result['description'].strip()[0:1000]} \n Score: {result['score']}")


def fixed_size_chunking(text, overlap, chunk_size=1000):
    """
    Chunk a given text into fixed size chunks.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size (otherwise step size would be zero)")
    words = text.split()
    chunks = []
    step_size = chunk_size - overlap
    for i in range(0, len(words), step_size):
        chunk_words = words[i:i+chunk_size]
        if len(chunk_words) <=overlap:
            break
        chunks.append(" ".join(chunk_words))
    return chunks

def semantic_chunking(text, overlap=0, max_chunk_size=4):
    """
    Chunk text on sentence boundaries to preserve meaning.
    Splits on sentence endings (. ! ?) and groups up to max_chunk_size sentences per chunk,
    with optional overlap of sentences between consecutive chunks.
    """
    if overlap >= max_chunk_size:
        raise ValueError("overlap must be less than max_chunk_size")
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return []
    chunks = []
    step_size = max_chunk_size - overlap
    for i in range(0, len(sentences), step_size):
        chunk_sentences = sentences[i : i + max_chunk_size]
        if not chunk_sentences:
            break
        chunks.append(" ".join(chunk_sentences))
    return chunks


def semantic_chunk_command(text, max_chunk_size=4, overlap=0):
    """
    Run semantic chunking and print chunk information.
    """
    chunks = semantic_chunking(text, overlap=overlap, max_chunk_size=max_chunk_size)
    print(f"Semantic chunking: {len(chunks)} chunks (max {max_chunk_size} sentences, overlap {overlap})")
    for i, chunk in enumerate(chunks):
        print(f"{i + 1}. {chunk}")


def chunk_text(query, overlap, chunk_size=200):
    """
    Chunk a given text into fixed size chunks.
    """
    chunks = fixed_size_chunking(query, overlap, chunk_size)
    print(f"chunking {len(chunks)} chunks")
    for i,chunk in enumerate(chunks):
        print(f"{i + 1}. {chunk}")
    