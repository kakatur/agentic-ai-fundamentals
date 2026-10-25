# 4.4 — Choosing the Right Vector Database: DuckDB, FAISS, Chroma, pgvector, Pinecone & Weaviate

## Learning outcome

Choose vector-search candidates by where retrieval runs, which features the workload needs, and which responsibilities your team wants to own. Follow five help-center articles through DuckDB SQL and an application-owned FAISS index, then compare pgvector, Chroma, Weaviate, and Pinecone. Apply five connected system-design questions covering storage, latency, freshness and access, operations, and total cost.

## DuckDB: embedded analytics and vector search

DuckDB is an embedded analytical database: SQL runs inside the host application's process without a separate database server. That process can run on a laptop, a cloud server, or a batch worker. DuckDB is useful for querying Parquet and CSV files directly, transforming datasets in batch pipelines, and combining SQL filtering with vector similarity calculations.

For retrieval, it can help inspect embedding matches, test filters, and build an exact-search baseline alongside ordinary data analysis. This lesson uses an in-memory DuckDB table so the setup and distance calculation are visible. Embedded deployment describes where the engine runs; it does not restrict DuckDB to a developer's laptop.

## Our five articles and their data contract

The question is **“Why was I charged twice?”** The input manifest, [`help_center/article_vectors.jsonl`](help_center/article_vectors.jsonl), uses JSON Lines (JSONL): one complete JSON object per line, without a surrounding array or commas between records. Its objects have exactly these four keys:

| Key | Meaning |
|---|---|
| `id` | Stable product-prefixed identifier, such as `billing-42`; also the Markdown filename stem |
| `name` | Display name, independent of the article body |
| `product` | Metadata used by the billing filter |
| `embedding` | Numeric vector used by both retrieval backends |

The lines keep the following order:

```jsonl
{"id": "account-73", "name": "Reset your password", "product": "account", "embedding": [0.0, 0.0, 1.0]}
{"id": "billing-42", "name": "Charged twice for the same purchase", "product": "billing", "embedding": [1.0, 0.0, 0.0]}
{"id": "billing-68", "name": "Change your payment method", "product": "billing", "embedding": [0.8, 0.6, 0.0]}
{"id": "billing-25", "name": "Check a refund", "product": "billing", "embedding": [0.9, 0.4358899, 0.0]}
{"id": "shipping-91", "name": "Find a delayed parcel", "product": "shipping", "embedding": [0.0, 1.0, 0.0]}
```

Each article body lives in `help_center/<id>.md`. For example, `account-73.md` contains password-reset instructions, while its name comes from the JSON object's `name` field. Markdown files contain body text only; the loader does not parse a heading or infer a title from the first line.

`load_records()` parses one JSON object per line in file order, reports malformed JSON or non-object records with their line numbers, checks that IDs are unique, reads the matching Markdown file, and builds each `SearchRecord`. The record keeps its explicit name, body, vector, product, source path, and embedding version. Search results use that explicit name too.

The demos share JSONL loading and query inputs in `article_data.py`. Run `demo_duckdb.py` for SQL search or `demo_faiss.py` for index search.

## Install and run

From this lesson directory:

```bash
python3 -m pip install -r requirements.txt
python3 demo.py
# Or run either search walkthrough separately:
python3 demo_duckdb.py
python3 demo_faiss.py
python3 -m unittest -v
```

`demo.py` runs both search walkthroughs and prints the interview scenario’s raw-vector storage estimate. `sizing.py` contains the storage calculation; it does not predict database capacity or latency.

`demo_duckdb.py` loads the five records, creates a DuckDB table, inserts the data, runs the SQL query, and prints the results. `demo_faiss.py` loads the same records into a FAISS index and prints its results. It does not require a separate DuckDB server or DuckDB CLI. The in-memory database is recreated each time you run the program.

## Create the DuckDB table and insert the records

The following Python statements can also be run interactively from the lesson directory. Keep the same Python session for the query in the next section.

```python
import duckdb
from article_data import load_records, QUERY_VECTOR, PRODUCT_FILTER

records = load_records()
connection = duckdb.connect(database=":memory:")
connection.execute("""
    CREATE TABLE articles (
        article_id VARCHAR,
        name VARCHAR,
        product VARCHAR,
        document VARCHAR,
        embedding FLOAT[]
    )
""")
rows = [
    (record.record_id, record.name, record.metadata["product"],
     record.document, list(record.embedding))
    for record in records
]
connection.executemany("INSERT INTO articles VALUES (?, ?, ?, ?, ?)", rows)
```

`FLOAT[]` holds each vector. `executemany` binds one row's five values to the five placeholders for each insert. The display name is inserted from `record.name`; the Markdown body is inserted separately into `document`.

For a persistent database, use `duckdb.connect(database="help_center.duckdb")` and manage table creation and repeated inserts deliberately. The lesson uses `:memory:` to keep each run independent.

## Run the vector-search SQL in DuckDB

```python
results = connection.execute("""
    SELECT article_id, name,
           list_cosine_distance(embedding, ?::FLOAT[]) AS cosine_distance
    FROM articles
    WHERE product = ?
    ORDER BY cosine_distance, article_id
    LIMIT 3
""", [list(QUERY_VECTOR), PRODUCT_FILTER["product"]]).fetchall()
for article_id, name, distance in results:
    print(f"{article_id}: {name} (cosine distance={distance:.3f})")
```

- `SELECT` returns the article ID, name, and calculated distance.
- `list_cosine_distance` compares the stored embedding with the query vector.
- Python supplies `QUERY_VECTOR` to the first placeholder and `"billing"` to the second. The `::FLOAT[]` cast gives the query vector its SQL type.
- `WHERE` restricts eligible records to billing.
- `ORDER BY` puts the smallest distance first, with article ID as a deterministic tie-breaker.
- `LIMIT 3` keeps the three closest eligible records; `fetchall()` returns them to Python.

Expected DuckDB output:

```text
billing-42: Charged twice for the same purchase (cosine distance=0.000)
billing-25: Check a refund (cosine distance=0.100)
billing-68: Change your payment method (cosine distance=0.200)
```

The duplicate-charge article is first. The password-reset and parcel articles are excluded by their product metadata. DuckDB scores every eligible row in this example; this exact scan does not use an approximate index. The zero distance is the closest match for these vectors.

## FAISS: an index inside your application

FAISS is a vector-search library that runs inside your application. It gives direct control over indexes while your application maps index results back to durable records. It can support semantic document search, finding similar images, and retrieval-index evaluation. The hosting process can run on a laptop or a production server.

Your team owns source documents, metadata, filtering, index persistence, recovery, and the API around the index. FAISS by itself does not supply a document database.

The existing `search_with_faiss()` function in `demo_faiss.py` creates a `FaissAdapter` using the query vector's dimension, calls `upsert()` for each record, and calls `search()` with the query vector, billing filter, and limit of three. The adapter maps integer labels back to `SearchRecord` objects; the result uses each hit's explicit `name` field.

Expected FAISS output:

```text
billing-42: Charged twice for the same purchase (squared L2 distance=0.000)
billing-25: Check a refund (squared L2 distance=0.200)
billing-68: Change your payment method (squared L2 distance=0.400)
```

The adapter uses an exact flat index with squared Euclidean distance. These vectors have unit length, so their result order agrees with cosine distance even though the scores differ. This tiny adapter retrieves the entire index and then applies the billing filter in application code. A production workload needs a tested filtering strategy; this example is not a latency, scale, or authorization design.

## pgvector: keep retrieval beside PostgreSQL data

pgvector adds vector storage and similarity search to PostgreSQL. If the help-center articles already live there, their vectors, metadata, and SQL filters can remain beside existing application data.

It can fit a support-search or recommendation feature that needs SQL joins with customer, product, or permission data. Exact search provides a baseline; approximate indexes are another option as the measured workload requires them. Evaluate query plans, filters, index maintenance, and capacity alongside existing database traffic.

## Chroma: retrieval records grouped in collections

Chroma is a dedicated vector database that groups record IDs, documents, embeddings, and metadata in collections. The application can retrieve matching document text through the same interface used for vector queries.

Example use cases include document assistants, searchable knowledge bases, and RAG prototypes that need retrieval records managed together. An embedded client can be a starting point, with server and managed deployment options for other needs. Metadata filters can restrict retrieval to a product category such as billing.

Chroma’s default Python embedding function uses `all-MiniLM-L6-v2` locally and may download its model files. You can configure another embedding function or supply your own vectors. Documents and queries must use compatible embeddings; changing models requires rebuilding the affected vectors. See Chroma embedding functions [https://docs.trychroma.com/docs/embeddings/embedding-functions].

## Weaviate: vector, keyword, and hybrid retrieval

Weaviate provides vector search, filtering, and hybrid search, with self-hosted and managed deployment options. Hybrid retrieval combines keyword and vector results.

A support knowledge base may need both the meaning of a question and exact product names or error codes. A product catalog may need structured-property filters before a similarity search. Evaluate Weaviate when those features belong in one retrieval service, then choose who will operate it.

## Pinecone: managed vector search

Pinecone is a managed vector-search service. Applications connect over the network while the provider operates the search infrastructure.

Example use cases include hosted knowledge assistants, semantic search, and recommendations. The application sends records and query vectors to an index and uses metadata filters to narrow results, such as searching billing records in this help center. Your team still owns source documents, embedding choices, access rules, and evaluation of relevance, latency, and cost.

For a multi-customer application, one namespace per tenant in a serverless index keeps records separate. The application must select the namespace from the authenticated tenant and enforce document permissions. See Pinecone multitenancy [https://docs.pinecone.io/guides/index-data/implement-multitenancy].

An application can also store conversation records and retrieve relevant details in later sessions to support agent memory, or match differently worded descriptions to catalog items. The application supplies the records and retrieval logic.

The repository's runnable comparison covers DuckDB and FAISS. The other backend sections explain deployment and use cases; they do not claim to provide tested SDK integrations here.

## Compare responsibilities and choose

| Option | What it provides | What your team still evaluates or owns |
|---|---|---|
| DuckDB | Embedded SQL analytics and exact vector scoring in this demo | Data/embedding pipeline, serving, and fit for the workload |
| FAISS | Vector indexes and similarity search inside the application | Records, filters, persistence, serving, and recovery |
| pgvector | Vector search beside relational PostgreSQL data | Query plans, capacity, index choice, and existing database workload |
| Chroma | Collections with retrieval records and metadata filters | Deployment, access policy, operations, and workload fit |
| Weaviate | Vector, keyword, hybrid search, and filtering | Deployment, operational ownership, and retrieval configuration |
| Pinecone | Managed vector-search infrastructure | Source data, access rules, embedding pipeline, network, and cost |

Start with the system's requirements: article count and growth, query volume, vector dimensions, strict filters, updates/deletes, freshness, relevance, latency, availability, and recovery. Compare candidates against the same records, model vectors, filters, and labeled queries. Keep source data, stable IDs, and embedding configuration available outside the index so a migration is a verifiable rebuild.

If the help center already uses PostgreSQL, pgvector is a natural candidate to evaluate first. Choose among candidates that meet the requirements, based on where retrieval should run and who will operate it. This lesson compares operating models; it does not establish a universal fastest or best backend.

## Tests and important limits

The tests check the ordered JSONL contract, stable product-prefixed IDs, headerless Markdown loading, explicit result names, DuckDB/FAISS billing results, vector dimensions, FAISS label-to-record mapping, updates and deletions, filtering before the result limit, and storage estimates. Lifecycle and filtering regression tests use the real FAISS library. The demo uses example illustrative data. It does not generate embeddings, benchmark relevance or latency, or exercise production access controls.

## Interview questions

These five questions follow one document-search platform. The numbers are hypothetical requirements, not backend capacity thresholds.

### 1. Basic — Vector database sizing

**The platform holds 100 million vectors, each with 1,536 dimensions, and expects 5× growth in two years. Before choosing a database, how would you estimate storage?**

A 32-bit float takes four bytes per dimension:

```text
100,000,000 × 1,536 × 4 = 614,400,000,000 bytes = 614.4 GB
5 × 614.4 GB = 3,072 GB = 3.072 TB
```

These are decimal units and count uncompressed vectors only. Article text, metadata, index structures, and replicas add storage. Compare the estimate with candidate memory and storage capacity, then evaluate compression or partitioning where needed. Raw vector size alone does not tell us how much RAM a deployment needs.

Run `python3 sizing.py` to reproduce both estimates. `estimate_raw_vector_bytes()` accepts a vector count, dimension count, and bytes per dimension; its default is four bytes for float32.

### 2. Intermediate — Latency and query load

**The same platform has 10,000 concurrent users and a P95 search-latency target below 100 ms. Is that enough information to choose a vector database?**

No. Concurrent users do not specify searches per second. Establish the query rate, burst traffic, number of returned matches, and how narrowly metadata filters restrict each search. P95 below 100 ms means at least 95% of requests must finish within that budget; define whether network time is included. Measure under representative load while records are added and updated. Use the same labeled queries and retrieval-quality target when comparing candidates so lower latency does not hide worse results.

### 3. Intermediate — Freshness and access

**Documents arrive continuously and must become searchable promptly. Searches must respect tenant boundaries and document-level permissions. What must you check before choosing the retrieval system?**

Specify a measurable arrival-to-searchable freshness target, plus deadlines for edits, deletions, and permission changes. Use the signed-in user’s verified identity to determine the tenant and permitted documents. Verify that results contain only text the user may access, including during continuous ingestion, document deletion, and access revocation. A product-category filter in this demo is not an authorization system.

### 4. Advanced — Operating model

**The application team can build retrieval features but cannot run search servers or handle database failover. Which operating model fits, and what must you check?**

Shortlist managed services such as Pinecone, Chroma Cloud, and Weaviate Cloud. Check who owns upgrades, monitoring, backups, and recovery, then review service commitments and recovery options. A self-managed database or custom FAISS service needs another team to operate it. The application team still owns the data pipeline and application access rules. Managed infrastructure alone does not establish the application’s availability or access correctness.

### 5. Advanced — Choose the best design

**Two proposals claim to meet search-latency and retrieval-quality targets. The platform requires 99.99% availability and expects 5× data growth in two years. How would you choose between them?**

Ask for test results supporting both claims. Verify access-control and freshness requirements as well. Check replication, failover, and recovery across the application and database against the availability target. Compare total cost, including storage, queries, data transfer, replicas, and engineering work. Estimate costs at the projected fivefold volume and confirm the team can operate and recover each design. Choose the design that meets all requirements at the lower total cost.

The local demo demonstrates exact retrieval and storage arithmetic. Load tests, ingestion freshness, tenant authorization, failover, and cost evaluation need a representative deployed workload; these five questions are an evaluation framework, not measured results from this fixture.

## References

- DuckDB array and list distance functions — https://duckdb.org/docs/current/sql/functions/array
- DuckDB vector similarity extension and limitations — https://duckdb.org/docs/current/core_extensions/vss
- FAISS index selection guidance — https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index
- pgvector project documentation — https://github.com/pgvector/pgvector
- Chroma deployment modes — https://docs.trychroma.com/docs/overview/architecture
- Weaviate deployment options — https://docs.weaviate.io/deploy
- Pinecone serverless index model — https://sdk.pinecone.io/python/how-to/indexes/serverless.html
