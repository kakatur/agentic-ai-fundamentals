# 04.01 - Understanding Embeddings: From Text to Vectors

## Learning outcome

Explain how an embedding model represents text as vectors, why meaning comes from relationships between vectors, and which configuration choices must match before vectors can be compared.

## Different words, related meaning

A user searches for "update my credentials," while the help center article is titled "reset your password." A keyword search may miss the article because the wording is different even though the intent is related.

An embedding model gives a retrieval system another representation to compare. It converts each piece of text into a fixed-length list of numbers called a **vector**.

## From text to vector space

You can picture a vector as a location in a mathematical space. A trained embedding model can place related text near other related text, even when the words do not match exactly.

The individual coordinates are not human-readable labels. One coordinate does not simply mean "password" or "account." The useful information comes from the relationship between complete vectors: their directions, distances, and relative positions.

An embedding does not understand text by itself. The model learned the vector space during training, and the retrieval system uses the resulting relationships.

## One model defines one space

Each embedding model defines its own coordinate system. Two models can both return vectors with 384 values while assigning different meaning to those coordinates. Equal dimensions therefore make vectors the same shape, but not necessarily comparable.

Documents and queries must be embedded into the same space. That normally means using the same model and version, input preparation, task or input type, dimensions, and normalization policy.

## Embedding configuration

Keep these choices explicit:

1. **Model and version** determine which learned vector space is used.
2. **Input preparation** includes prefixes, task types, truncation, and other model-specific processing.
3. **Dimension** determines the number of coordinates in each vector.
4. **Normalization** optionally rescales vectors before comparison.

The first three choices determine what is produced and whether vectors share a coordinate system. Normalization changes how the vectors are prepared for a similarity metric, which lesson 4.2 explores in detail.

## Using a trained embedding model

You can use a trained embedding model in two common ways:

- Call a hosted API. The provider runs the model and returns the vector.
- Download a model from Hugging Face and run it on your own machine or server.

In either case, read the model's instructions for input prefixes, task types, dimensions, and normalization. Use the same model and configuration for indexed documents and incoming queries.

## Code walkthrough

The lesson uses a deterministic token-hashing embedder so the mechanics remain visible:

- `EmbeddingConfig` records the model ID and version, input type, dimension, and normalization policy.
- `TokenHashEmbedder.embed` converts text into a repeatable fixed-length vector.
- `assert_compatible` rejects vectors created with different configurations.
- `dot` checks dimensions before comparing vectors.

Token hashing is not a semantic model. It can demonstrate the pipeline, configuration, and vector shape, but it has not learned that "credentials" and "password" may be related. Use a trained embedding model when evaluating semantic retrieval quality.

## Demo and tests

The demo embeds a query and documents with one shared configuration. It prints the configuration, vector length, and repeatable comparison scores.

The tests verify that:

- the same text and configuration produce repeatable vectors;
- every vector has the configured dimension;
- normalized nonzero vectors have unit length;
- incompatible configurations and dimensions fail explicitly.

Never repair a dimension mismatch by padding or trimming a vector. That changes its coordinates without placing it in the expected vector space.

For a practical companion on embedding contracts, retrieval evaluation, and model migrations, read [From Text to Vectors: Understanding How Embeddings Work](https://medium.com/@kakatur/from-text-to-vectors-understanding-how-embeddings-work-3b48a5fef71b).

## Interview questions

### Basic

What is an embedding?

An embedding is a numerical representation of an input. For text embeddings, the relationships between complete vectors can capture useful relationships between pieces of text.

### Intermediate

Why can two vectors with the same dimension still be incompatible?

Dimension describes the number of coordinates, not what those coordinates mean. Vectors from different models may belong to different learned spaces.

### Advanced

What makes two embeddings safe to compare?

They should come from the same model and version with compatible input preparation, task type, dimensions, and normalization. If the embedding space changes, create and evaluate a separate index rather than mixing the vectors.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
