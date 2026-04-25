# 🧠 RAG Support Chatbot

```
  ╔══════════════════════════════════════════════════════╗
  ║   Your docs don't have to be dead weight anymore.   ║
  ║         Ask them questions. Get real answers.        ║
  ╚══════════════════════════════════════════════════════╝
```

> Built with LangChain · ChromaDB · Groq Llama · HuggingFace · BM25

---

## 🤔 The Problem This Solves

You have documents. PDFs, markdown files, support wikis.

Someone asks *"what's the refund policy?"* and you either:
- Dig through 12 files manually 😤
- Ask a generic LLM that just... makes something up 😬

**This project does neither.**

It reads your documents, remembers them, and answers questions using *only what's actually written* — no hallucination, no guessing.

---

## ⚡ How It Works

```
  You ask a question
        │
        ▼
  ┌─────────────────────────────┐
  │      Hybrid Retriever       │
  │  ┌───────────┐ ┌─────────┐  │
  │  │  Vector   │ │  BM25   │  │
  │  │  Search   │ │ Search  │  │
  │  │  (60%)    │ │  (40%)  │  │
  │  └───────────┘ └─────────┘  │
  └─────────────────────────────┘
        │
        ▼
  Best matching chunks
        │
        ▼
  Groq Llama 3.3 70B
        │
        ▼
  Grounded, accurate answer ✅
```

Two retrieval strategies work together so nothing slips through the cracks:
- **Vector search** catches *semantically similar* content
- **BM25** catches *exact keyword* matches

---

## 🗂 Project Structure

```
rag-support-chatbot/
│
├── 📁 docs/                  ← Drop your .md files here
│
├── 📁 vector_db/
│   └── rag_pipeline.py       ← Hybrid RAG chain lives here
│
├── ingest.py                 ← Run once to index your docs
├── main.py                   ← Chat entry point
├── .env                      ← Your GROQ_API_KEY goes here
└── requirements.txt
```

---

## 🚀 Getting Started

**1. Clone & install**
```bash
git clone https://github.com/your-username/rag-support-chatbot
cd rag-support-chatbot
pip install -r requirements.txt
```

**2. Add your API key**
```bash
# .env
GROQ_API_KEY=your_key_here
```

**3. Drop your documents**
```bash
# Add .md files into the docs/ folder
cp your-support-docs.md docs/
```

**4. Index them**
```bash
python ingest.py
```

**5. Start chatting**
```bash
python main.py
```

---

## 💬 Example Session

```
────────────────────────────────────
  RAG Support Chatbot  |  ask away
────────────────────────────────────

You: What is the refund policy?

Bot: According to the documentation, refunds are processed
     within 7 business days of cancellation. Subscriptions
     cancelled mid-cycle are eligible for a pro-rated refund...

You: What happens if I miss a payment?

Bot: If a payment fails, the system retries after 3 days.
     After two failed attempts, the account is paused...
────────────────────────────────────
```

---

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| Framework | LangChain |
| Vector Store | ChromaDB |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| LLM | Groq · Llama 3.3 70B Versatile |
| Keyword Search | BM25 Retriever |
| Env Management | python-dotenv |

---

## 🔭 What's Next

- [ ] 🌐 Streamlit web UI
- [ ] 🔁 Query rewriting for better retrieval
- [ ] 📊 Reranking with cross-encoders
- [ ] 💬 Multi-turn conversation memory
- [ ] 📁 Support for PDF and DOCX ingestion

---

## 👨‍💻 Author

**Tarun Dange** — AI & Data Science

Building RAG systems, LLM pipelines, and tools that make documents actually useful.

---

*If this helped you — drop a ⭐. It takes 2 seconds and makes the commit history feel less lonely.*
