from lib.llm import answer_question
from lib.hybrid_search import HybridSearch
from lib.search_utils import load_movies


def rag(query):
    movies = load_movies()
    hs = HybridSearch(movies)
    rrf_result = hs.rrf_search(query=query, limit=5, k=0.5)
    rag_results = answer_question(query, rrf_result)
    print("Search results:")
    for res in rrf_result:
        print(f"- {res['title']}")
    print("rag response")
    print(rag_results)
