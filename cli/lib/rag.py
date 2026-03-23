from lib.llm import answer_question, summarize, citations
from lib.hybrid_search import HybridSearch
from lib.search_utils import load_movies


def rag(query):
    """Perform retrieval-augmented generation for a given query.

    Runs a hybrid RRF search over the movie dataset and passes the top 5
    results to the LLM to generate an answer.

    Args:
        query (str): The natural language question to answer.
    """
    movies = load_movies()
    hs = HybridSearch(movies)
    rrf_result = hs.rrf_search(query=query, limit=5, k=0.5)
    rag_results = answer_question(query, rrf_result)
    print("Search results:")
    for res in rrf_result:
        print(f"- {res['title']}")
    print("rag response")
    print(rag_results)


def rag_summarize(query, limit):
    """Perform retrieval-augmented generation and summarize the results.

    Runs a hybrid RRF search over the movie dataset and passes the retrieved
    results to the LLM to produce a concise summary.

    Args:
        query (str): The natural language query to search and summarize.
        limit (int): Maximum number of search results to retrieve.
    """
    movies = load_movies()
    hs = HybridSearch(movies)
    rrf_result = hs.rrf_search(query=query, limit=limit, k=0.5)
    summarize_results = summarize(query, rrf_result)
    print("search results")
    for res in rrf_result:
        print(f"{res['title']}")
    print("Rag summarize result")
    print(summarize_results)


def citations_llm(query, limit):
    movies = load_movies()
    hs = HybridSearch(movies)
    rrf_result = hs.rrf_search(query=query, limit=limit, k=0.5)
    citations_results = citations(query, rrf_result)
    print("search results")
    for res in rrf_result:
        print(f"{res['title']}")
    print("LLm citations")
    print(citations_results)
