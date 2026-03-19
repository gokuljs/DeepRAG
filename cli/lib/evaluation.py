from .search_utils import golden_dataset, load_movies
from .hybrid_search import HybridSearch


def evaluate(limit):
    
    test_cases = golden_dataset()
    movies = load_movies()
    hs = HybridSearch(movies)
    print(f"limit {limit}")
    for test_case in test_cases:
        query = test_case["query"]
        relevant_docs = test_case["relevant_docs"]
        rrf_results = hs.rrf_search(query,k= 60, limit=limit)
        relevant_count = 0
        for result in rrf_results:
            relevant_count += result["title"] in relevant_docs 
            
        print(f"relevant_count: {relevant_count}")    
        precision = relevant_count / limit
        retrived = ','.join([result["title"] for result in rrf_results])
        recall = relevant_count / len(relevant_docs)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        print(f"query: {query}")
        print(f"Precision@{limit}: {precision}")
        print(f"Recall@{limit}: {recall}")
        print(f"F1 Score@{limit}: {f1_score}")
        print(f"Retrived: {retrived}")
        print(f"Relevant: {relevant_docs}")
    
        