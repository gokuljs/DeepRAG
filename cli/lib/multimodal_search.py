from PIL import Image
from sentence_transformers import SentenceTransformer


class MultimodalSearch:
    """Multimodal search using CLIP to embed images and text into a shared vector space."""

    def __init__(self, model_name="clip-ViT-B-32"):
        """Initialize the multimodal search with a CLIP model.

        Args:
            model_name: Name of the SentenceTransformer CLIP model to use.
        """
        self.model = SentenceTransformer(model_name)

    def embed_image(self, image_path):
        """Generate a vector embedding for an image using CLIP.

        Args:
            image_path: Path to the image file.

        Returns:
            A numpy array representing the image embedding.
        """
        image = Image.open(image_path)
        return self.model.encode([image])[0]


def verify_image_embedding(image_fpath):
    """Quick sanity check that prints the embedding dimensionality for a given image.

    Args:
        image_fpath: Path to the image file to verify.
    """
    ms = MultimodalSearch()
    embedding = ms.embed_image(image_fpath)
    print(f"Embedding shape: {embedding.shape[0]} dimensions")
