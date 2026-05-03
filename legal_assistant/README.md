# AI Legal Assistant — Pakistan Laws (CSV-based RAG)

A Streamlit chatbot that answers questions about Pakistan laws using a **local CSV dataset** and a Retrieval-Augmented Generation (RAG) pipeline powered by Google Gemini.

No Supabase, no internet database required — just your API key and the CSV file.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your Groq API key to `.env`
```
GROQ_API_KEY="your_key_here"
```
Get a free key at: https://aistudio.google.com/app/apikey

### 3. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 4. Initialize the knowledge base
Click **"Initialize Knowledge Base"** in the sidebar once. The FAISS index is saved locally — subsequent runs load it automatically.

---

## Project Structure
```
legal_assistant/
├── app.py                  # Streamlit UI
├── requirements.txt
├── .env                    # API key (not committed)
├── .gitignore
│
├── data/
│   └── pakistan_laws.csv   # 65 curated legal sections
│
├── backend/
│   ├── ingest.py           # CSV loader & text chunker
│   ├── vector_store.py     # FAISS build / save / load
│   ├── retriever.py        # Semantic search
│   └── pipeline.py         # RAG orchestration
│
└── llm/
    ├── gemini_api.py        # Gemini LLM wrapper
    └── prompts.py           # System prompt templates
```

---

## Dataset (data/pakistan_laws.csv)

65 curated sections covering:

| Category | Examples |
|---|---|
| Pakistan Penal Code | Theft, Murder, Robbery, Fraud, Kidnapping |
| Constitution | Fundamental rights, Equality, Free speech |
| Criminal Procedure Code | Bail, FIR, Arrest, Trial procedure |
| Muslim Family Laws | Marriage, Divorce, Khul, Mehr, Custody |
| Tenant / Rent Laws | Eviction, Rent agreements, Security deposit |
| Labor Laws | Minimum wage, Overtime, Termination, EOBI |
| Islamic Banking | Murabaha, Ijara, Musharaka |
| Cyber Crime | PECA 2016 — fraud, harassment, stalking |
| Consumer Rights | Defective goods, Misleading ads |
| Property Laws | Registration, Stamp duty, Land acquisition |

### Adding More Laws
Simply add rows to `data/pakistan_laws.csv` with columns:
```
id, title, category, section_number, content
```
Then click **"Initialize Knowledge Base"** again to rebuild the index.

---

## Example Questions

**English:**
- What are the bail conditions?
- What is the punishment for theft in Pakistan?
- What are tenant rights?
- How does Islamic banking Murabaha work?
- What are worker rights regarding overtime?

**Urdu:**
- ضمانت کی شرائط کیا ہیں؟
- چوری کی سزا کیا ہے؟
- کرایہ دار کے حقوق کیا ہیں؟
- طلاق کا طریقہ کار کیا ہے؟
