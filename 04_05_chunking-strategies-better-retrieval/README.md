# 4.5 — Chunking Strategies for Vector Similarity Search

## Learning outcome

Compare fixed word windows, sentence chunks, and paragraph chunks with heading metadata. Inspect how each strategy changes the text available to vector similarity search, then choose a chunking strategy that keeps the evidence needed to answer an agent’s question.

## One refund procedure, three chunking strategies

Let’s say we’re building an internal application that helps customer service agents find answers in company documents. The app includes a refund procedure with the heading “Refunds after a duplicate charge”:

```text
Refunds after a duplicate charge
First, confirm that both transactions have settled. Then refund the duplicate charge and tell the customer the refund should appear within five business days.
```

While helping a customer, an agent searches: **“A customer was charged twice. What steps should I follow, and what refund timing should I tell them?”** Each strategy presents different text to vector similarity search:

| Chunking strategy | What becomes one searchable record | What to inspect |
|---|---|---|
| Fixed word window | A fixed number of words, optionally repeated across neighboring windows | Does a chunk split separate a condition, action, or timing from the rest of the procedure? |
| Sentence | One sentence at a time | Does the matching sentence say which issue it applies to? |
| Paragraph with heading metadata | The paragraph is searchable; the heading is carried separately as metadata | Does returned metadata preserve useful topic context? |

Vector similarity search ranks embedded chunk text against the agent’s question. Chunking determines what information each searchable record contains. For this procedure, the paragraph chunk contains the settlement condition, refund action, and timing; its heading is carried separately as metadata and does not affect similarity unless the application also includes it in the embedding input.

Each demo chunk carries `document_id`, `document_title`, `chunk_index`, and `section_heading` metadata. These fields identify and organize the source; the heading stays out of the searchable chunk text.

The procedure is written for the agent, who uses it to help the customer. A retrieved passage should include enough of the internal instructions to guide the agent’s next steps.

In a retrieval system, distinguish the searched chunk from the context returned to the agent and the evidence used to evaluate the result:

- **Search chunk:** the passage embedded and ranked for the agent’s question.
- **Returned context:** the text passed to the application or language model after a match.
- **Evaluation evidence:** the complete procedure needed to answer the question.

These can differ. For example, embed a sentence as the search chunk, then use its parent section ID to return the full refund procedure as context. If multiple matched sentences point to that same section, return the section once. This keeps search focused while giving the agent the transaction validation, refund action, and timing together.

## What the comparison teaches

| Strategy | What this example preserves | What to consider |
|---|---|---|
| Fixed windows | Similar-sized records and a clear baseline | A chunk split can separate the refund action from its timing |
| Sentence chunks | Complete steps in concise search records | Carry the heading when it names the topic or condition |
| Paragraph with heading metadata | The full procedure in the text, with its topic label in metadata | Review how much of the section each question needs |
| Overlapping windows | Repeated text across chunk splits | More vectors and potentially duplicate search results |
| Parent-child retrieval | A focused match can return its containing section | Requires parent links and a context-return policy |

Choose a strategy based on document structure and the details agents need to retrieve. For this example, a sentence chunk is precise but can lose its subject; paragraph text keeps the full procedure together, while heading metadata preserves its topic label for the application. For longer manuals, carry heading paths and table headers into metadata or use parent sections to return the surrounding context. Check the embedding model's token limit before embedding each chunk.

A quick quality check is to read a candidate chunk by itself: can the agent tell what topic it covers, what action to take, and what condition or timing matters? The transaction-validation sentence states the condition; the paragraph chunk keeps the procedure together, and its heading metadata preserves the topic label for the application. Use this check to see how much of the procedure a passage makes clear.

## Run the comparison

Requires Python 3.11 or newer. Install the dependencies first; the embedding
model downloads on the first run.

Run the demo from this directory:

```bash
python3 -m pip install -r requirements.txt
python3 demo.py
```

The program applies three strategies to the same internal procedure, embeds each
search chunk with a local Sentence Transformers model, and stores its vector,
text, ID, and metadata in an in-memory DuckDB table. It embeds the agent question
with the same model, ranks each strategy's chunks by cosine similarity, and
prints up to two results per strategy. This is an exact vector search over the
small demo table; it does not need an approximate-nearest-neighbor index. The
DuckDB table is rebuilt on each run. Read each result beside its score and
metadata to see which parts of the procedure the chunk contains.

The demo then compares eight-word windows over the procedure body with no
overlap and with three-word overlap. For this procedure, the body forms three
chunks without overlap and five with overlap; this part shows the chunks and
counts, without embedding the overlapping variant. For fixed windows, the
printed chunk IDs encode the start and exclusive end word offsets.

With this example query, the top sentence chunk contains the refund action and timing but omits the transaction validation. The paragraph result contains the validation, action, and timing together, while the heading is returned as metadata. That is the specific context trade-off to look for in your own documents.

Try changing `QUERY` in `demo.py` and rerun it to compare all three strategies with the same question. You can also change the fixed window size. The sentence splitter uses a simple punctuation rule for this example; production text may require a splitter that handles abbreviations and other language-specific boundaries. For production, set the chunk token budget with the selected embedding model's tokenizer, then evaluate retrieved context, answer coverage, and latency on representative questions.

## A small chunking implementation

The reusable fixed-window baseline is in `chunking.py`. Its `chunk_text` function accepts source text, a stable source ID, a word-window size, optional overlap, and optional metadata. It returns chunk IDs, start/end word offsets, and metadata. `demo.py` adds sentence and paragraph chunking, carrying document titles and section headings as metadata.

```bash
python3 demo.py
python3 -m unittest -v
```

Use this implementation to inspect what overlap repeats and how offsets are recorded. Compare overlap on representative agent questions: check whether the condition stays with the action, then record vector count and duplicate result rate. Preserve document structure and set the production token budget with the selected model's tokenizer.

## Keep chunks traceable

Give each chunk a stable ID derived from a source ID, source revision, and chunk position or content hash. Record enough information to recover:

- source ID and source revision;
- chunker and embedding configuration versions;
- heading path or parent ID;
- source offsets or page location;
- content hash and the text actually embedded.

Traceability lets you inspect why a chunk matched and rebuild it when its source changes. Include the source revision or content hash in stable IDs so each chunk remains tied to its source as the document changes.

## Evaluate the whole retrieval path

Use the same refund procedure with questions that test different details: “A customer was charged twice. What steps should I follow, and what refund timing should I tell them?”, “Do both transactions need to have settled before I issue the refund?”, and “What refund timing should I give the customer?” These test the procedure as a whole, its settlement condition, and its timing. For other documents, build similar questions for a heading plus an instruction, a numbered procedure, a table row, and repeated matches within one parent section.

For each agent question, record the rank of the relevant search chunk, whether returned context contains the complete instruction, and the duplicate result rate. Compare embedding count, context length, latency, and storage across strategies. Smaller chunks make passages more specific and often need context expansion to return all steps; overlap carries words across splits and adds vectors. Use representative questions to choose the chunk size and overlap that fit the application.

When chunking changes, create a separately versioned index from the original source documents. Replay the labeled evaluation set you established in Lesson 4.4, add questions whose relevant information is split across chunks, and inspect changed failures before moving traffic with a rollback path. Chunking changes the records being searched, so revisit the backend results using the final chunk design. Mixing incompatible chunk strategies in one unexplained index makes results difficult to diagnose.

## Practical checks

- Set chunk budgets with the selected model's tokenizer.
- Carry headings, list labels, and table headers as metadata or embedding input when chunks need that context.
- Compare overlap using retrieval quality, duplicate result rate, and vector storage.
- Return the parent section when a focused child match needs surrounding instructions.
- Compare a versioned index with a fixed question set before using it for agent searches.

## Interview questions

### Basic

**Why split long documents before embedding them?**

A document may contain unrelated topics, exceed the model's input limit, or return too much context. Smaller chunks let the system rank a focused passage.

### Intermediate

**What does overlap trade?**

It repeats some text across chunk splits, which can preserve context. That increases stored vectors and can create duplicate results, so measure the benefit and cost.

### Advanced

**What chunking strategies have you used, and what practical tips helped you choose and tune them?**

For fixed-size chunking, I split by the embedding model’s token budget and compare overlap settings, because overlap can preserve context across chunk boundaries, but also adds vectors and can crowd results with duplicates.

For sentence-based chunking, I keep sentences intact for focused matches and preserve parent-section links so retrieval can return more context when needed.

For structure-aware chunking, I follow headings, paragraphs, and section boundaries, but still check token counts because a well-structured section can exceed the model’s limit.

I test them on realistic user questions and choose the approach that returns relevant, complete context within our storage and response-time limits.

## References

- Sentence Transformers semantic search and model input guidance — https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html
- all-MiniLM-L6-v2 model card and input behavior — https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- DuckDB array cosine similarity — https://duckdb.org/docs/current/sql/functions/array
- DuckDB in-memory Python connection — https://duckdb.org/docs/stable/clients/python/overview
- Pinecone, “Chunking Strategies for LLM Applications” — https://www.pinecone.io/learn/chunking-strategies/
