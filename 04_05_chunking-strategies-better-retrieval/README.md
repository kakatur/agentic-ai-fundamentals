# 4.5 — Chunking Strategies for Vector Similarity Search

## Learning outcome

Compare fixed word windows, sentence chunks, and heading-plus-paragraph chunks. Inspect how each strategy changes the text available to vector similarity search, then choose a chunking strategy that keeps the evidence needed to answer an agent’s question.

## One refund procedure, three chunking strategies

Let’s say we’re building an internal application that helps customer service agents find answers in company documents. The app includes a refund procedure with the heading “Refunds after a duplicate charge”:

```text
Refunds after a duplicate charge
First, confirm that both transactions have settled. Then refund the duplicate charge and tell the customer the refund should appear within five business days.
```

While helping a customer, an agent searches: **“A customer was charged twice. What steps should I follow, and what refund timing should I tell them?”** Each strategy presents different text to vector similarity search:

| Chunking strategy | What becomes one searchable record | What to inspect |
|---|---|---|
| Fixed word window | A fixed number of words, optionally repeated across neighboring windows | Does a chunk split separate the heading from the procedure? |
| Sentence | One sentence at a time | Does the matching sentence say which issue it applies to? |
| Heading plus paragraph | A heading and its paragraph together | Does the larger record add useful context or unrelated text? |

Vector similarity search ranks embedded chunks against the agent’s question. Chunking determines what information each searchable record contains. For this procedure, a heading-plus-paragraph chunk gives search one candidate containing the topic, settlement condition, refund action, and timing; sentence chunks make each step available as a focused passage.

The procedure is written for the agent, who uses it to help the customer. A retrieved passage should include enough of the internal instructions to guide the agent’s next steps.

In a retrieval system, distinguish the searched chunk from the context returned to the agent and the evidence used to evaluate the result:

- **Search chunk:** the passage embedded and ranked for the agent’s question.
- **Returned context:** the text passed to the application or language model after a match.
- **Evaluation evidence:** the complete procedure needed to answer the question.

These can differ. For example, embed a sentence as the search chunk, then use its parent section ID to return the full refund procedure as context. If multiple matched sentences point to that same section, return the section once. This keeps search focused while giving the agent the settlement check, refund action, and timing together.

## What the comparison teaches

| Strategy | What this example preserves | What to consider |
|---|---|---|
| Fixed windows | Similar-sized records and a clear baseline | A chunk split can detach the heading from the action it describes |
| Sentence chunks | Complete steps in concise search records | Carry the heading when it names the topic or condition |
| Heading plus paragraph | The topic and its explanation in one record | Review how much of the section each question needs |
| Overlapping windows | Repeated text across chunk splits | More vectors and potentially duplicate search results |
| Parent-child retrieval | A focused match can return its containing section | Requires parent links and a context-return policy |

Choose a strategy based on document structure and the details agents need to retrieve. For this example, a sentence chunk is precise but can lose its subject; the heading-plus-paragraph chunk keeps both subject and procedure. For longer manuals, carry heading paths and table headers into chunks or use parent sections to return the surrounding context. Check the embedding model's token limit before embedding each chunk.

A quick quality check is to read a candidate chunk by itself: can the agent tell what topic it covers, what action to take, and what condition or timing matters? The settlement sentence states the condition; the heading-plus-paragraph chunk brings the topic, condition, and refund action together. Use this check to see how much of the procedure a passage makes clear.

## Run the comparison

Run the demo from this directory:

```bash
python3 demo.py
```

The program applies three strategies to the same internal procedure and agent question, prints the top two chunks for each, and reports how many question words appear in each chunk. Read each result beside its score to see which parts of the question and procedure the chunk contains. It then compares eight-word windows with no overlap and with a three-word overlap. For this procedure, overlap keeps “First, confirm that” at the start of the next chunk and increases the chunk count from four to six. The code also prints stable IDs and source word offsets for fixed windows.

With this example query, the top sentence chunk contains the refund action and timing but omits the settlement check. The heading-plus-paragraph result contains the topic, precondition, action, and timing together. That is the specific context trade-off to look for in your own documents.

Try changing the fixed window size in `demo.py` and compare the returned text for the same agent question. For production, set the chunk token budget with the selected embedding model's tokenizer, then evaluate retrieved context, answer coverage, and latency on representative questions.

## A small chunking implementation

The reusable fixed-window baseline is in `chunking.py`. Its `chunk_text` function accepts source text, a stable source ID, a word-window size, and optional overlap. It returns chunk IDs and start/end word offsets. `demo.py` adds sentence and heading-plus-paragraph chunking to show how source structure changes the records.

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
- Carry headings, list labels, and table headers into chunks that need that context.
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

**How would you choose a chunking strategy for an internal support application?**

Inspect the company documents’ headings, steps, tables, and the answers agents need; preserve links to source locations; then compare candidate strategies on questions affected by chunk splits, contextual completeness, duplicate result rate, latency, and storage.

## References

- Sentence Transformers semantic search and model input guidance — https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html
- all-MiniLM-L6-v2 model card and input behavior — https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Pinecone, “Chunking Strategies for LLM Applications” — https://www.pinecone.io/learn/chunking-strategies/
