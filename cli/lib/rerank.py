import os
from dotenv import load_dotenv
from google import genai
from numpy import promote_types
from .search_utils import PROMPTS_DIR

load_dotenv()
MODEL = "gemini-2.5-flash"

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")
client = genai.Client(api_key=api_key)

def individual_rerank(query, documents):
    with open(PROMPTS_DIR / "individual_rerank.md", "r") as f:
        prompt = f.read()
    results =[]
    for doc in documents:
        _prompt = prompt.format(query=query, title = doc["title"], description = doc["description"])
        response = client.models.generate_content(model=MODEL, contents=_prompt)
        score = response.text.strip() if response.text else None
        if not score or not score.isdigit():
            print(f"Warning: unexpected response for '{doc['title']}': {score!r} — defaulting to 0")
            rerank_score = 0
        else:
            rerank_score = int(score)
        results.append({**doc, "rerank_response": rerank_score})
        print(f"Title: {doc['title']} - Rerank Response: {rerank_score}")
    result = sorted(results, key=lambda x: x["rerank_response"], reverse=True)
    return results
