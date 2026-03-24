import argparse
import mimetypes
from pathlib import Path

from lib.llm import describe_image

SCRIPT_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(
        description="Multi modal image search description")
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to an image file for multi modal search in rag",
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Text query to rewrite based on the image",
    )
    args = parser.parse_args()

    image_path = SCRIPT_DIR / args.image if not Path(args.image).is_absolute() else Path(args.image)
    mime, _ = mimetypes.guess_type(str(image_path))
    mime = mime or "image/jpeg"

    with open(image_path, "rb") as f:
        img = f.read()

    response = describe_image(img, mime, args.query)

    print(f"Rewritten query: {response.text.strip()}")
    if response.usage_metadata is not None:
        print(f"Total tokens:    {response.usage_metadata.total_token_count}")


if __name__ == "__main__":
    main()
