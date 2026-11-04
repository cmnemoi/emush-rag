# Project Brief

## What it is

- Ask NERON: a RAG API answering questions about the game [eMush](https://emush.eternaltwin.org/), from the community wikis.
- Serves the Ask NERON chat frontend (`askneron.netlify.app`, another repo) at `api.askneron.cmnemoi.com`.

## Why it exists

- eMush rules are scattered across several wikis: players get a sourced answer in their own language instead of searching each one.

## Domain language

| Term | Meaning |
| ---- | ------- |
| NERON | the in-game ship AI the assistant plays; the persona of `SYSTEM_PROMPT` |
| Document | a wiki page (`content` plus `title`, `link`, `source`), split into chunks before indexing |
| Indexation | scrape the wikis, split, embed, and load a new version of the vector store |
| Reformulation | rewriting the question with the chat history into a standalone question before retrieval |
| Index alias | `emush_rag`, the name the API reads; it points to the published index version |

## Key features

- Answer a question with its chat history, returning the answer and the retrieved documents.
- Hybrid retrieval: keywords for exact game terms, embeddings for meaning.
- Weekly reindexation of the freshly scraped wikis, with zero-downtime switch and rollback.
- Per-IP rate limiting on the questions endpoint.
- Traces and metrics in Grafana.
