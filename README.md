# DeepRAG

A movie search engine demonstrating advanced Retrieval-Augmented Generation (RAG) techniques — keyword search, semantic search, hybrid fusion, reranking, and evaluation.

---

## System Architecture

```mermaid
flowchart TD
    subgraph INGEST["📥 Ingestion Pipeline (Offline)"]
        RAW[Raw Documents]
        CLEAN[Text Cleaning\nStrip noise, normalize whitespace]
        CHUNK[Chunking\nFixed size / Sentence / Semantic]

        subgraph KW_INDEX["Keyword Index"]
            STEM[Tokenize → Lowercase\nRemove Stopwords → Stem]
            INVERT[Inverted Index\nBM25 / TF-IDF weights]
        end

        subgraph VEC_INDEX["Vector Index"]
            EMBED[Embedding Model\nall-MiniLM-L6-v2]
            VECSTORE[Vector Store\nNumPy .npy cache]
        end

        RAW --> CLEAN --> CHUNK
        CHUNK --> STEM --> INVERT
        CHUNK --> EMBED --> VECSTORE
    end

    subgraph QUERY_PIPE["🔍 Query Pipeline (Online)"]
        Q([User Query])

        subgraph Q_ENHANCE["Query Enhancement — Gemini 2.5 Flash"]
            SPELL[Spell Correct]
            REWRITE[Query Rewrite]
            EXPAND[Query Expansion\nSynonyms + related terms]
        end

        subgraph RETRIEVAL["Retrieval"]
            KW_SEARCH[Keyword Search\nBM25 — exact term match\nfast and interpretable]
            SEM_SEARCH[Semantic Search\nCosine similarity over chunks\nmeaning-based and fuzzy]
        end

        subgraph FUSION["Result Fusion"]
            RRF[Reciprocal Rank Fusion\nCombine ranked lists\nno score normalization needed]
            WEIGHTED[Weighted Blend\nα × keyword + 1-α × semantic\nrequires score normalization]
        end

        subgraph RERANK["Re-ranking"]
            CROSS[Cross-Encoder\nScore query+doc pairs jointly\nmore accurate, slower]
            LLM_RR[LLM Reranker\nGemini scores or sorts docs\nmost powerful, most expensive]
        end

        subgraph GENERATE["Generation"]
            CONTEXT[Build Context\nTop-K chunks as prompt]
            LLM[LLM Response]
            ANS([Final Answer])
        end

        Q --> Q_ENHANCE --> RETRIEVAL
        INVERT --> KW_SEARCH
        VECSTORE --> SEM_SEARCH
        KW_SEARCH --> FUSION
        SEM_SEARCH --> FUSION
        FUSION --> RERANK --> CONTEXT --> LLM --> ANS
    end

    subgraph EVAL["📐 Evaluation"]
        GOLDEN[Golden Dataset\nQuery + Relevant Docs]
        METRICS[Precision@K · Recall@K · F1@K]
        GOLDEN --> METRICS
        ANS -.->|compare| METRICS
    end
```

---

## Pipeline Stages

| Stage | What happens | Why it matters |
|---|---|---|
| **Chunking** | Split docs into smaller pieces | LLMs have context limits; smaller chunks = more precise retrieval |
| **Keyword Index** | Tokenize, stem, build inverted index with BM25 weights | Fast exact-term matching, great for names and acronyms |
| **Vector Index** | Encode chunks into dense embeddings | Captures meaning even when words don't match exactly |
| **Query Enhancement** | LLM corrects, rewrites, or expands the query | Better query = better retrieval results |
| **Fusion** | Merge two ranked lists (RRF or weighted blend) | Combines strengths of both retrieval methods |
| **Reranking** | Re-score top-N with a heavier model | Cheap retrieval finds candidates; expensive model picks the best |
| **Generation** | Top chunks stuffed into LLM prompt | The actual answer generation step |
| **Evaluation** | Compare results against known ground truth | Measures whether any of this is actually working |

---

## Search Types

| Type | Algorithm | Strength |
|---|---|---|
| Keyword (BM25) | Term frequency + inverse document frequency | Exact matches, fast |
| Semantic (Full-doc) | Cosine similarity on full-document embeddings | Meaning-based matching |
| Semantic (Chunked) | Cosine similarity on sentence chunks, max-pooled per doc | More precise semantic hits |
| Hybrid Weighted | Min-max normalize both → `α·BM25 + (1-α)·semantic` | Tunable balance |
| Hybrid RRF | `Σ 1/(k + rank)` across both retrievers | Robust, no normalization needed |

---

## Stack

- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Reranker:** `cross-encoder/ms-marco-TinyBERT-L2-v2`
- **LLM:** Google Gemini 2.5 Flash (query enhancement + LLM reranking)
- **Corpus:** ~25k movies with titles and descriptions
