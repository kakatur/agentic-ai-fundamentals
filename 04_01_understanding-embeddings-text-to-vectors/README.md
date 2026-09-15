# 4.1 - How Text Embeddings Match Meaning Beyond Keywords

## Learning outcome

Build a small semantic-search baseline that downloads a specific Sentence Transformers model version, converts a query and documents into embeddings, and ranks the documents by similarity.

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
text -> model preparation -> 384-value embedding -> similarity score -> ranking
```

The code encodes the query and the candidate documents, compares the query vector with each document vector, and sorts the resulting cosine scores. An embedding does not make the final decision by itself. Your application still chooses the documents, ranking policy, and relevance threshold. Lesson 4.2 explains the similarity math in detail.

## Code walkthrough

The implementation keeps model-specific code at one boundary:

1. `load_model` supplies the model ID and exact revision to `SentenceTransformer`.
2. `embed_texts` validates the text and selects `encode_query` or `encode_document` for its role.
3. The model returns normalized vectors, and the function verifies the expected 384-value dimension.
4. `rank_documents` checks the query and document roles, calculates cosine similarity, and sorts the results.
5. `exact_token_overlap` supplies a deliberately small keyword baseline for contrast.

The revision pin makes the lesson output reproducible. The demo simply downloads and runs that exact model.

## What the demo proves

[`demo.py`](demo.py) makes the complete path visible:

- Sentence Transformers loads the real model from Hugging Face or its local cache;
- the model produces a 384-dimensional vector for the query and each document;
- the keyword baseline finds no shared tokens for the controlled examples;
- the embedding ranking places the password-reset article first.

The demo does not expose every internal transformer operation, and it does not prove that this model is best for every corpus. Evaluate candidate models with representative queries, documents, and relevance judgments from your own application.

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
