# Hybrid Search for RAG: Combining Vector and Keyword Search

Build a small retrieval pipeline that searches support documents by meaning and by terms, then combines the two rankings. You will inspect the candidates and learn why a hybrid result still needs evaluation before it is supplied to a language model.

## The problem

A support question may say “my password reset link doesn't work” while the useful document says “the password reset token has expired.” Vector search can find a relationship even when the wording differs. Another question may contain `E104`, where the exact characters matter. Keyword search can find that identifier. Neither method guarantees relevance: a vector model can confuse similar topics, and a keyword match can miss a paraphrase.

Here, each record is a document with a stable ID, collection, and body. The example embeds the body with `sentence-transformers/all-MiniLM-L6-v2` and stores the resulting 384-dimensional vector in DuckDB with the text and model name. The query is encoded with the same model. DuckDB computes cosine similarity over its stored vectors; the model, not DuckDB, creates those vectors. DuckDB's full-text extension provides the BM25 ranking. The example uses an exact vector scan on a tiny corpus, not an approximate index.

## Follow the data

1. `demo.py` creates the sample documents and encodes their text. `build` stores each vector with its ID, text, collection, and model, then creates a full-text index.
2. For a query, `search` checks the model and applies the same collection filter to both searches. Vector search orders eligible rows by cosine similarity. Keyword search orders BM25 matches by score.
3. Each search returns a limited list of candidates. `fuse` adds reciprocal rank contributions for each ID, and the demo prints the two search lists and the fused list. A document absent from both lists cannot appear in the final result.

The corpus includes an internal document with an error code. The collection filter keeps it out of the support results. This illustrates consistent filtering, not a complete authorization system: a production service must enforce the caller's actual access policy before exposing results.

## How rank fusion works

The BM25 and cosine scores are on different scales. Reciprocal rank fusion (RRF) combines rank positions instead of adding those raw numbers. For each candidate, add `1 / (k + rank)` for each list in which it appears. Ranks start at one. With `k = 60`, a document ranked first in one list and third in the other receives `1/61 + 1/63`, approximately `0.0323`. A missing candidate contributes zero for that search. Larger `k` makes differences between positions smaller. The example breaks score ties by document ID and counts an ID only once per search.

RRF avoids directly comparing score scales but discards score gaps: it treats a narrow first-place lead and a large one alike. Candidate depth and `k` affect the output. Neither RRF nor hybrid search guarantees a better ranking for every query.

## Inspect the example

Run the demo and compare the printed IDs and scores for each search. Their positions in each list show their ranks. The queries cover a paraphrase, an identifier, and a mixed query. Look at the original document text to decide whether the ordering makes sense. The model and its library versions can change the scores and ordering; do not treat these few examples as a benchmark.

The validated demo produces these top results:

| Query | Vector search | Keyword search | Hybrid search using RRF |
|---|---|---|---|
| `My password reset link doesn't work` | `reset` | `reset` | `reset` |
| `E104` | `e105` | `e104` | `e104` |
| `E104 password reset link expired` | `e104` | `e104` | `e104` |

For the code-only query, vector search puts `e104` second; keyword search finds it as its only match. Its RRF score is `1/62 + 1/61 ≈ 0.0325`, so hybrid search puts it first. This is the observed result for this corpus and model, not a general accuracy guarantee.

The full-text index is a snapshot. Rebuild it when the source text changes; the demo replaces the corpus and index together. Its index configuration preserves digits so an identifier such as `E104` is not reduced to a letter. Tokenization still needs testing for real identifiers containing punctuation, case variations, or non-English text.

## Move toward production

Create a labeled query set with paraphrases, identifiers, mixed questions, and difficult negatives. Compare keyword-only, vector-only, and hybrid results under the same eligibility rules, using metrics such as recall at the candidate cutoff and a ranking metric appropriate to your labels. Inspect regressions by query type along with latency and cost. Tune candidate depth and fusion settings on development queries and reserve separate queries for evaluation.

Version the embedding model, its revision, dimensions, and input construction. Re-embed when those change, and keep the text, vectors, and search indexes consistent. The exact scan is simple for a small local dataset; for larger or concurrent workloads, measure it and consider an indexed vector service or DuckDB's experimental VSS extension where its operational constraints fit. Apply access filters in both searches and test them independently. Retrieval is evidence selection, not proof that an answer is correct.

## Beyond the demo

The demo returns ranked documents. A full chatbot can optionally rerank these results with a cross-encoder that reads the query and each candidate document together and assigns a new relevance score. The chatbot then supplies selected document text and the question to its language model to generate an answer. RRF combines existing rankings; a cross-encoder examines the actual text. The demo implements neither reranking nor answer generation.

RRF is one way to combine results. OpenSearch's normalization processor also supports normalizing each search's scores and combining them with a weighted arithmetic mean. This lets you control how much each search influences the ranking. Choose the method and weights using representative queries. When keyword search returns nothing, RRF already preserves the vector results' order; a different fusion method alone does not supply missing evidence.

When long documents are split into chunks, a chunk such as “Request a new reset link” may be separated from its product, version, or error code. Adding that source-grounded context before both embedding and BM25 indexing can make the chunk easier to find. Check the added context against the source document and evaluate the results. The small demo uses document snippets directly and does not implement chunking or contextual enrichment.

## Interview questions

**Basic: Why combine vector and keyword search?** They capture different signals: similarity in embedding space and lexical matches. They can find complementary candidates, but their benefit depends on the data and queries.

**Intermediate: Why use RRF?** It combines ranks without assuming BM25 and cosine scores have comparable scales. Its trade-off is that it ignores the magnitude of score differences.

**Advanced: How would you diagnose a missing relevant document?** Check access filters and indexing first, then each search's candidate list and cutoff, then fusion ranks. Evaluate on labeled query slices and measure latency before adjusting depth or weights.

## Run and test

Python 3 and network access are required for the initial package, model, and DuckDB extension downloads. The demo uses an in-memory DuckDB database. Each run builds the documents, embeddings, and full-text index; closing the connection discards them without creating a database file.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
python -m unittest -v
```

Validation used Python 3.14.7, DuckDB 1.5.6, and sentence-transformers 5.7.0. The dependency ranges allow other versions; their scores and ordering may differ.

The tests use synthetic vectors to check fusion, filtering, and input validation without downloading the embedding model. The DuckDB full-text extension must be installed or available locally.

## References

- DuckDB full-text search and BM25: https://duckdb.org/docs/1.5/core_extensions/full_text_search
- DuckDB array similarity: https://duckdb.org/docs/1.5/sql/functions/array
- DuckDB VSS: https://duckdb.org/docs/1.5/core_extensions/vss
- Sentence Transformers model: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Reciprocal rank fusion paper: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
- DuckDB in-memory connections: https://duckdb.org/docs/1.5/clients/python/dbapi
- OpenSearch normalization and weighted score combination: https://docs.opensearch.org/latest/search-plugins/search-pipelines/normalization-processor/
- OpenSearch cross-encoder reranking: https://docs.opensearch.org/latest/search-plugins/search-pipelines/rerank-processor/
- Anthropic contextual retrieval: https://www.anthropic.com/research/contextual-retrieval
