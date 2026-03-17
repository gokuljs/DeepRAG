import os
import json
from dotenv import load_dotenv
from google import genai
from numpy import promote_types
from .search_utils import PROMPTS_DIR
from sentence_transformers import CrossEncoder

load_dotenv()
MODEL = "gemini-2.5-flash"

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")
client = genai.Client(api_key=api_key)
cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L2-v2")

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

def batch_rerank(query, documents):
    with open(PROMPTS_DIR / "batch_rerank.md", "r") as f:
        prompt = f.read()
    results =[]
    movie_template= '''<movie idx="{idx}"> {title}: \n {desc} \n</movie>'''
    doc_list_str = ""
    for idx, doc in enumerate(documents):
        doc_list_str+=movie_template.format(idx=idx, title=doc["title"], desc=doc["description"])
    
    _prompt = prompt.format(query=query, doc_list_str=doc_list_str)
    response = client.models.generate_content(model=MODEL, contents=_prompt)
    print("==="*10)
    print(response.text)
    print("==="*10)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    response_parsed = json.loads(raw)
    results =[]
    for idx, doc in enumerate(documents):
        results.append({**doc,**{"rerank_score":response_parsed.index(int(idx))}})
    result = sorted(results, key=lambda x: x["rerank_score"], reverse=False)
    return result
    

def cross_encoder_rerank(query, documents):
    pairs = []
    for doc in documents:
        pairs.append([query, f"{doc.get('title', '')} - {doc.get('description', '')}"])
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L2-v2")
    scores = cross_encoder.predict(pairs)
    results =[]
    for idx, doc in enumerate(documents):
        results.append({**doc,**{"cross_encoder_score":scores[idx]}})
    result = sorted(results, key=lambda x: x["cross_encoder_score"], reverse=True)
    print(f"Cross Encoder Reranked {len(results)} results")
    print(result[:2])
    return result
    