# 4.1 - Create Your First Text Embedding in Minutes

## Learning outcome

Build a small semantic-search baseline that downloads a specific Sentence Transformers model version, first encodes a fixed set of documents into an in-memory collection, then encodes a search query and ranks the stored document vectors by similarity.

## The answer can be relevant without sharing a keyword

A user searches a help center for `I can't log in`. An article says `Reset your password to regain account access.` The two texts share no exact tokens, so a minimal keyword-overlap check returns an empty set.

A sentence embedding model offers another signal. It maps each text to a fixed-length vector, allowing the application to compare the full numerical representations even when the wording changes.

The specific model version used in this lesson produces the following result:

```text
query: "I can't log in"

keyword overlap:
  []           Reset your password to regain account access.

embedding ranking:
  +0.582       Reset your password to regain account access.
  +0.054       Download last quarter's revenue report.
  -0.097       Track a package that is out for delivery.
```

These scores belong to this model revision and these exact inputs. They demonstrate the lesson example, not a universal quality benchmark or relevance threshold.

## Meet the model used in the demo

The demo uses [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It is a compact sentence-transformer model designed to encode sentences and short paragraphs for tasks such as semantic search, clustering, and sentence similarity.

The model maps each input to a vector containing 384 values. That number is the vector's **dimension**. You can picture the complete vector as one location in the model's learned embedding space. A given number in the vector usually does not have a stable human-readable meaning; the useful signal comes from relationships between complete vectors.

The model card reports that the model was fine-tuned with a contrastive objective on more than one billion sentence pairs. During that training, related examples were pulled closer together and unrelated examples were pushed farther apart. That training helps the model place differently worded but related texts near one another.

The first time you run the demo, Sentence Transformers downloads this specific model version from Hugging Face. After that, it uses the local cache. Inputs longer than 256 word pieces are truncated by this model, so use it for sentences and short paragraphs or chunk longer documents before encoding them.

## Framework: text becomes a ranking signal

```text
When documents are added or changed:
document -> encode once -> keep text and vector in an index

For each search:
query -> encode -> compare with indexed document vectors -> ranked results
```

In a deployed search system, the document vectors are usually persisted in a vector database as documents are ingested or updated. Each search encodes the new query, then asks the database to find nearby stored vectors. The database can return the matching text or references and metadata for the application to use.

This lesson keeps the same two phases but uses a Python list of vectors in memory instead of a vector database. The three fixed documents are encoded once when the script starts, then reused for the query comparison. The list is rebuilt on every run, and the demo scans all three vectors directly. An embedding does not make the final relevance decision by itself; evaluate ranking with examples from your application. Lesson 4.2 explains normalization and similarity math in detail.

## Code walkthrough

The implementation keeps model-specific code at one boundary:

1. `load_model` supplies the model ID and exact revision to `SentenceTransformer`.
2. `build_in_memory_index` calls `embed_texts` once for the fixed document set, using `encode_document`; the vectors stay in memory for this run.
3. `search` calls `embed_texts` for each search query, using `encode_query`, then compares it with the existing document vectors.
4. The model returns normalized vectors, and `embed_texts` verifies the expected 384-value dimension.
5. `rank_documents` checks the query and document roles, calculates cosine similarity against every in-memory document vector, and sorts the results.
6. `exact_token_overlap` supplies a deliberately small keyword baseline for contrast.

The revision pin makes the lesson output reproducible. The demo simply downloads and runs that exact model.

## What the demo proves

[`demo.py`](demo.py) makes the complete path visible:

- Sentence Transformers loads the real model from Hugging Face or its local cache;
- the script builds an in-memory collection by producing a 384-dimensional vector for each fixed document;
- each search produces a query vector and compares it with those existing document vectors;
- the keyword baseline finds no shared tokens for the controlled examples;
- the embedding ranking places the password-reset article first.

The demo does not use a vector database: it rebuilds its small in-memory collection each time it runs and scans every vector. A real application normally persists document vectors during ingestion so later searches only need to encode the query. The demo does not expose every internal transformer operation, and it does not prove that this model is best for every corpus. Evaluate candidate models with representative queries, documents, and relevance judgments from your own application.

## Tests and failure conditions

[`test_lesson.py`](test_lesson.py) uses a tiny offline fixture so the unit tests remain fast and deterministic. It verifies:

- query and document encoding;
- the zero-overlap keyword baseline;
- the expected semantic ranking;
- rejection of an unexpected output dimension;
- ordinary cosine-similarity input checks;
- rejection of blank text and unsupported roles.

Common mistakes:

- **Using the demo score as a production threshold:** tune ranking behavior with labeled examples from your application.
- **Re-encoding the whole corpus for every search:** prepare vectors when documents are added or changed, persist them in an index, and encode each incoming query separately. This small demo rebuilds an in-memory collection once per program run to avoid introducing database setup.
- **Sending long documents as one input:** this model truncates beyond 256 word pieces; chunk longer material first.
- **Ignoring the model's retrieval methods:** use `encode_query` and `encode_document` when the library and model expose those roles.
- **Assuming embeddings make the product decision:** retrieval scores are inputs to application policy, evaluation, and often downstream processing.

## Decision checklist

Before adapting the demo, record:

- the exact model ID and revision;
- the output dimension and input-length limit;
- how queries and documents are prepared;
- the similarity metric;
- representative evaluation queries and relevance judgments.

## Interview questions

### Basic

**What is a text embedding?**

A fixed-length numerical representation produced by a model. For this model, each sentence or short paragraph becomes a 384-dimensional vector, and relationships between complete vectors provide a useful signal for semantic ranking.

### Intermediate

**What happens the first time this Python demo loads the model?**

Sentence Transformers downloads the files for the specified model revision from Hugging Face and stores them in its local cache. Later runs can load those cached files.

### Advanced

**What should you check before using `all-MiniLM-L6-v2` on long documents?**

The model truncates input longer than 256 word pieces. Split long documents into meaningful chunks and evaluate retrieval quality on examples from the target application.

## Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 demo.py
python3 -m unittest -v
```

The unit tests use an offline fixture. `demo.py` uses the specified public model revision and needs network access on its first run.
