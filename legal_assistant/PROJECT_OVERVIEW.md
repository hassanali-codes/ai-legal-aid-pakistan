# ⚖️ AI Legal Assistant — Pakistan Laws
### Intelligent Legal Q&A System with RAG + Multilingual Support

---

## 1. Project Overview

The **AI Legal Assistant** is an intelligent chatbot built for Pakistani citizens and legal professionals. It allows users to ask questions about Pakistani laws in **English, Urdu (script), or Roman Urdu** and receive accurate, cited legal answers — instantly, for free, without needing a lawyer for basic queries.

The system uses **Retrieval-Augmented Generation (RAG)**: it first searches a curated legal knowledge base, then feeds the most relevant sections to an LLM that generates a grounded, cited answer.

> "Access to justice starts with access to information."

---

## 2. Problem Statement

- Ordinary citizens in Pakistan often **don't know their legal rights**
- Hiring a lawyer for basic legal queries is **expensive and inaccessible**
- Legal documents are written in complex language, difficult to understand
- No reliable, free, bilingual (Urdu + English) legal information tool exists
- People frequently face issues around bail, tenant rights, divorce, labor rights — **without knowing the law**

---

## 3. Proposed Solution

An AI-powered legal assistant that:

| Feature | Description |
|---|---|
| 🔍 Semantic Search | Finds the most relevant law sections for any question |
| 🤖 AI-Generated Answers | Provides plain-language explanations with law citations |
| 🌐 Multilingual | Understands and replies in English, Urdu script, or Roman Urdu |
| 📚 Knowledge Base | 65+ curated sections from 10 major Pakistani laws |
| 💻 Web Interface | Clean, accessible Streamlit UI with dark/light theme |
| ⚡ Fast & Free | Runs locally, no subscription required |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Web Browser)                    │
│              Streamlit UI — localhost:8501               │
└────────────────────────┬────────────────────────────────┘
                         │ Question (Eng / Urdu / Roman)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                          │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐   ┌────────────┐  │
│  │   Retriever  │───▶│ Prompt Builder│──▶│  Groq LLM  │  │
│  │ (FAISS Search│    │  (prompts.py) │   │(LLaMA 3.1) │  │
│  │  Top-5 docs) │    └──────────────┘   └────────────┘  │
│  └──────┬───────┘                                        │
│         │                                                │
│  ┌──────▼───────┐                                        │
│  │  FAISS Index │                                        │
│  │ (Vector Store│                                        │
│  │  + Embeddings│                                        │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────┘
                         │ Cited Answer
                         ▼
                    Back to User
```

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Streamlit 1.35+ | Web UI, chat interface |
| **LLM** | Groq API → LLaMA 3.1 8B Instant | Answer generation |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Text vectorization |
| **Vector Store** | FAISS (Facebook AI Similarity Search) | Semantic retrieval |
| **RAG Framework** | LangChain 0.2+ | Pipeline orchestration |
| **Data** | Local CSV (65 legal sections) | Knowledge base |
| **Language** | Python 3.10+ | Core language |
| **Config** | python-dotenv | API key management |
| **Styling** | Custom CSS + Google Fonts (Cinzel, Inter, Noto Nastaliq Urdu) | UI theming |

---

## 6. RAG Pipeline — Step by Step

### Step 1 — Ingestion (`backend/ingest.py`)
- Reads `data/pakistan_laws.csv`
- Each row is converted into a rich text chunk:
  ```
  Law: Pakistan Penal Code
  Category: Criminal Law
  Section: 379

  Whoever commits theft shall be punished with imprisonment...
  ```

### Step 2 — Vectorization (`backend/vector_store.py`)
- Each chunk is passed through `all-MiniLM-L6-v2` (HuggingFace) to produce a 384-dim embedding
- All embeddings are stored in a **FAISS index** saved locally to `faiss_index/`
- On subsequent runs, the index is loaded from disk automatically — no reprocessing needed

### Step 3 — Retrieval (`backend/retriever.py`)
- User's question is embedded using the same model
- FAISS performs **cosine similarity search** and returns the **Top-5** most relevant legal sections

### Step 4 — Prompt Building (`llm/prompts.py`)
- Retrieved sections are formatted as structured context
- Injected into a system prompt with strict rules:
  - Answer only from provided context
  - Cite law name + section number
  - Reply in user's exact language (English / Urdu / Roman Urdu)

### Step 5 — Generation (`llm/gemini_api.py`)
- Prompt is sent to **Groq API** running **LLaMA 3.1 8B Instant**
- Response is streamed back and displayed in the chat UI

---

## 7. Multilingual Support

The assistant detects the language/script of each question and responds accordingly:

| Input Language | Response Language | Example |
|---|---|---|
| English | English | "What are the bail conditions?" |
| Urdu Script | Urdu Script | "ضمانت کی شرائط کیا ہیں؟" |
| Roman Urdu | Roman Urdu | "Bail ki shartein kya hain?" |
| Roman English | Roman English (casual) | "bhai overtime ka kya hukum hai?" |

This is enforced strictly in the system prompt — the model never switches scripts.

---

## 8. Dataset — Pakistan Laws CSV

**File:** `data/pakistan_laws.csv`
**Total Sections:** 65 curated legal sections
**Columns:** `id, title, category, section_number, content`

| # | Category | Key Laws Covered |
|---|---|---|
| 1 | Pakistan Penal Code (PPC) | Theft (S.379), Murder (S.302), Robbery (S.390), Fraud, Kidnapping |
| 2 | Constitution of Pakistan | Article 9 (Right to Life), Article 14 (Dignity), Article 25 (Equality), Free Speech |
| 3 | Criminal Procedure Code (CrPC) | Bail, FIR procedure, Arrest rights, Trial process |
| 4 | Muslim Family Laws Ordinance | Marriage, Divorce (Talaq), Khula, Mehr, Child Custody |
| 5 | Tenant / Rent Laws | Eviction rules, Rent agreements, Security deposit rights |
| 6 | Labor & Worker Rights | Minimum wage, Overtime pay, Wrongful termination, EOBI pension |
| 7 | Islamic Banking Laws | Murabaha, Ijara, Musharaka contracts |
| 8 | Cyber Crime (PECA 2016) | Online fraud, Harassment, Stalking, Defamation |
| 9 | Consumer Rights | Defective goods, Misleading advertisements |
| 10 | Property Laws | Land registration, Stamp duty, Compulsory acquisition |

### Extending the Dataset
Add new rows to the CSV — no code changes needed:
```csv
id,title,category,section_number,content
66,Income Tax Ordinance,Tax Law,S.114,"Every person whose income exceeds..."
```
Then click **"Initialize Knowledge Base"** to rebuild the index.

---

## 9. UI Features

### Sidebar
- **Appearance Toggle** — Switch between dark/light theme
- **System Status** — Shows Groq API and Knowledge Base status with color-coded pills
- **Initialize Knowledge Base** — One-click FAISS index build
- **Clear Chat** — Reset conversation
- **Covered Laws** — Quick reference tags for all 10 law categories

### Main Area
- **Hero Card** — Title with Urdu subtitle, status pills
- **Floating Theme Toggle** — Fixed button top-right beside Deploy button (☀️ / 🌙)
- **Chat Bubbles** — User messages in blue, AI responses in gold-bordered glass cards
- **Bot Avatar** — Gold circular ⚖️ avatar for assistant messages
- **Chat Input** — Supports Urdu, English, and Roman Urdu input
- **Empty State** — Guided prompt when no conversation started

### Themes
| Dark Mode | Light Mode |
|---|---|
| Deep navy background (#0b0f1a) | Warm parchment (#f4f1ea) |
| Gold accents (#d4af37) | Amber-gold accents (#92710a) |
| Glass-effect bot bubbles | White bot bubbles with soft shadow |
| Radial glow hero card | Light cream hero card |

---

## 10. Project File Structure

```
legal_assistant/
│
├── app.py                   ← Main Streamlit UI + theme logic
├── requirements.txt         ← All Python dependencies
├── .env                     ← GROQ_API_KEY (not committed to git)
├── .gitignore
├── README.md
├── PROJECT_OVERVIEW.md      ← This file
│
├── data/
│   └── pakistan_laws.csv    ← 65 curated legal sections (knowledge base)
│
├── faiss_index/
│   ├── index.faiss          ← Binary FAISS vector index
│   └── index.pkl            ← Document metadata pickle
│
├── backend/
│   ├── __init__.py
│   ├── ingest.py            ← CSV loader → text chunks
│   ├── vector_store.py      ← FAISS build / save / load
│   ├── retriever.py         ← Top-K semantic search
│   └── pipeline.py          ← Full RAG orchestration
│
└── llm/
    ├── __init__.py
    ├── gemini_api.py        ← Groq API wrapper (LLaMA 3.1)
    └── prompts.py           ← System prompt + language rules
```

---

## 11. How to Run

### Prerequisites
- Python 3.10+
- Groq API key (free at https://console.groq.com)

### Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key in .env
echo GROQ_API_KEY=your_key_here > .env

# 3. Run the app
streamlit run app.py
```

### First Run
1. Open http://localhost:8501
2. Click **"⚡ Initialize Knowledge Base"** in the sidebar
3. Wait ~10 seconds for the FAISS index to build
4. Start asking questions!

---

## 12. Example Interactions

### English
> **Q:** What is the punishment for theft in Pakistan?
> **A:** Under Section 379 of the Pakistan Penal Code, theft is punishable by imprisonment of up to 3 years, a fine, or both. [PPC S.379]

> **Q:** What are the bail conditions?
> **A:** Under Section 496 of the CrPC, bail is a right for bailable offences. For non-bailable offences, the court considers flight risk, severity of the crime, and prior record. [CrPC S.496-497]

### Urdu Script
> **Q:** طلاق کا طریقہ کار کیا ہے؟
> **A:** مسلم فیملی لاز آرڈیننس 1961 کے تحت، طلاق کے لیے یونین کونسل کو تحریری نوٹس دینا ضروری ہے۔ نوٹس کے 90 دن بعد طلاق نافذ ہوتی ہے۔ [MFLO 1961]

### Roman Urdu
> **Q:** Bail ki shartein kya hain?
> **A:** CrPC Section 496-497 ke mutabiq, bailable jurm mein bail ka haq hai. Non-bailable mein court decide karta hai ke mulzim bhaag toh nahi jaega aur jurm kitna sangeen hai. [CrPC S.496]

---

## 13. Key Design Decisions

| Decision | Reason |
|---|---|
| Local CSV instead of cloud DB | No subscription cost, works offline, easy to extend |
| FAISS instead of cloud vector DB | Fast, free, runs entirely on local machine |
| HuggingFace embeddings (MiniLM) | Free, no API quota, 384-dim is sufficient for legal text |
| Groq API (LLaMA 3.1 8B) | Extremely fast inference, generous free tier |
| Streamlit for UI | Rapid development, Python-native, no frontend skills needed |
| Strict language prompt | Prevents the LLM from mixing scripts mid-answer |

---

## 14. Limitations & Future Improvements

### Current Limitations
- Knowledge base is limited to 65 sections (manually curated)
- No real-time law updates — dataset must be manually maintained
- Cannot handle highly complex multi-law cross-referencing cases
- No user authentication or conversation history persistence
- Answers are informational only — not a substitute for legal counsel

### Planned Improvements
| Feature | Description |
|---|---|
| 📄 PDF Upload | Let lawyers upload new legal documents directly |
| 🔄 Auto-update | Scrape official Pakistan legal gazette for updates |
| 🗣️ Voice Input | Accept spoken Urdu questions |
| 📱 Mobile App | React Native wrapper around the Streamlit API |
| 👤 User Accounts | Save chat history per user |
| 🌍 Multi-jurisdiction | Extend to other South Asian legal systems |
| 📊 Analytics | Track most-asked questions to improve the dataset |

---

## 15. Team & Credits

| Role | Contribution |
|---|---|
| AI/ML Engineer | RAG pipeline, embeddings, LLM integration |
| Backend Developer | Data ingestion, vector store, retrieval logic |
| Frontend Developer | Streamlit UI, CSS theming, dark/light modes |
| Legal Researcher | Curated and verified the 65 legal sections |

**Models & Libraries Used:**
- Meta LLaMA 3.1 8B (via Groq)
- sentence-transformers/all-MiniLM-L6-v2 (HuggingFace)
- FAISS (Meta AI)
- LangChain
- Streamlit

---

## 16. Impact & Use Cases

| User | Use Case |
|---|---|
| 👨‍👩‍👧 General Public | Know your rights before approaching police, landlord, or employer |
| 🧑‍🎓 Law Students | Quick reference for case studies and exam preparation |
| ⚖️ Junior Lawyers | Fast lookup of relevant sections during client consultations |
| 🏢 HR Departments | Check labor law compliance (overtime, termination, EOBI) |
| 🏠 Tenants / Landlords | Understand rent laws and eviction procedures |
| 💑 Families | Understand family law (divorce, custody, mehr, inheritance) |

---

*Built with ❤️ for accessible justice in Pakistan.*
*"قانون سب کے لیے ہے" — The law is for everyone.*
