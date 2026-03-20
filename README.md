# DeepRAG


---

## System Architecture

```mermaid
flowchart TD
    Q([🧑 User Query]) --> QPRE

    subgraph QPRE["🧹 Query Preprocessing"]
        direction TB
        QP1[Spell Correction\nfix typos before retrieval]
        QP2[Query Rewrite\nLLM rephrases for better searchability]
        QP3[Query Expansion\nadd synonyms + related terms]
        QP4[Tokenize\nsplit into individual tokens]
        QP5[Lowercase\nnormalize case]
        QP6[Remove Punctuation\nstrip special characters]
        QP7[Remove Stopwords\ndrop the, is, and, of ...]
        QP8[Stemming / Lemmatization\nrunning → run, movies → movi]
        QP1 --> QP2 --> QP3 --> QP4 --> QP5 --> QP6 --> QP7 --> QP8
    end

    subgraph DOCPRE["📄 Document Preprocessing — Offline / Index Time"]
        direction TB
        D0[Raw Documents]
        D1[Text Cleaning\nstrip HTML, normalize whitespace]
        D2[Chunking\nsentence windows with overlap]
        D3[Tokenize → Lowercase\nRemove Punctuation → Stopwords → Stem\nsame pipeline as query side]
        D4[Embed Chunks\nall-MiniLM-L6-v2 → .npy cache]
        D5[Build Inverted Index\ntoken → doc posting list\nBM25 weights stored]
        D0 --> D1 --> D2 --> D3
        D3 --> D4
        D3 --> D5
    end

    QPRE --> KW & SEM

    subgraph KW["🔑 Keyword Search"]
        direction TB
        K1[Lookup tokens in Inverted Index]
        K2[TF-IDF Scoring]
        K3[BM25 Scoring\nk1=1.5  b=0.75]
        K1 --> K2 --> K3
    end

    subgraph SEM["🧠 Semantic Search"]
        direction TB
        S1[Encode Query → dense vector]
        S2[Cosine Similarity vs chunk embeddings]
        S3[Max-Pool per Document]
        S1 --> S2 --> S3
    end

    D5 --> KW
    D4 --> SEM

    KW --> FUSION
    SEM --> FUSION

    subgraph FUSION["🔀 Hybrid Fusion"]
        direction TB
        F1[Weighted Blend\nα × BM25 + 1-α × Semantic]
        F2[Reciprocal Rank Fusion\nΣ 1 / k + rank]
        F1 & F2 --> F3[Top-N Candidates]
    end

    FUSION --> RR

    subgraph RR["📊 Reranking"]
        direction TB
        R1[Cross-Encoder\njointly scores query + doc]
        R2[LLM Individual\nGemini scores each doc 0–10]
        R3[LLM Batch\nGemini ranks all in one call]
        R1 & R2 & R3 --> R4[Final Ranked Results]
    end

    RR --> OUT([✅ Top-K Output])
    OUT --> EVAL

    subgraph EVAL["📐 Evaluation"]
        direction TB
        E1[Golden Dataset\n10 queries with ground truth] --> E2[Precision@K] & E3[Recall@K] --> E4[F1@K]
    end
```

---

## Key Insight — Query and Document Use the Same Preprocessing

Both sides go through **tokenize → lowercase → remove punctuation → remove stopwords → stem**. This symmetry is critical — if the query is stemmed to `movi` but the index was built from unstemmed `movies`, there would be zero matches. Both sides must speak the same language.

---

## Layer Breakdown

### 🧹 Query Preprocessing
| Step | What it does |
|---|---|
| Spell Correction | Fix typos before they ruin retrieval |
| Query Rewrite | LLM rephrases query to be more searchable |
| Query Expansion | Add synonyms and related terms to widen recall |
| Tokenize | Split query string into individual tokens |
| Lowercase | Normalize case so `Movie` and `movie` match |
| Remove Punctuation | Strip characters like `.`, `!`, `?` |
| Remove Stopwords | Drop high-frequency words with no signal |
| Stemming | Reduce words to root form — `running → run` |

### 📄 Document Preprocessing
| Step | What it does |
|---|---|
| Text Cleaning | Strip HTML tags, normalize whitespace |
| Chunking | Split into overlapping sentence windows |
| Same normalization | Exact same tokenize → stem pipeline as query |
| Embed Chunks | Encode each chunk into a 384-dim vector |
| Inverted Index | Build BM25-weighted token → document mapping |

### 🔑 Keyword Search
| Step | What it does |
|---|---|
| Inverted Index Lookup | Find all docs containing query tokens |
| TF-IDF | Score by term frequency × rarity |
| BM25 | Length-normalize so long docs don't dominate |

### 🧠 Semantic Search
| Step | What it does |
|---|---|
| Encode Query | Convert query to dense vector |
| Cosine Similarity | Compare query vector against all chunk vectors |
| Max-Pool per Doc | Best chunk score represents the whole document |

### 🔀 Hybrid Fusion
| Method | How it works |
|---|---|
| Weighted Blend | Normalize both to 0–1, then blend with α |
| RRF | Rank-based — robust to score scale differences |

### 📊 Reranking
| Method | Tradeoff |
|---|---|
| Cross-Encoder | Most accurate, scores pairs jointly |
| LLM Individual | Flexible, one Gemini call per doc |
| LLM Batch | Fastest, one Gemini call for all docs |

### 📐 Evaluation
| Metric | Formula |
|---|---|
| Precision@K | relevant hits ÷ K |
| Recall@K | relevant hits ÷ total relevant docs |
| F1@K | 2 × P × R ÷ (P + R) |

---

## Stack

| Component | Tool |
|---|---|
| Bi-encoder | `sentence-transformers/all-MiniLM-L6-v2` |
| Cross-encoder | `cross-encoder/ms-marco-TinyBERT-L2-v2` |
| LLM | Google Gemini 2.5 Flash |
| Corpus | ~25k movies with titles and descriptions |
