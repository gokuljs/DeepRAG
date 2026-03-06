from sentence_transformers import SentenceTransformer


class SemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def generate_embeddings(self, text: str):
        """
        Generate embeddings for a given text.
        """
        if text is None or text.strip() == "":
            raise ValueError("Text cannot be None or empty")
        return self.model.encode([text])[0]

def verify_model(model_name: str = 'all-MiniLM-L6-v2'):
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
