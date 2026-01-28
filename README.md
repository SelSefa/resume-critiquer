# Resume Critiquer (Streamlit + OpenAI)

A minimal Streamlit app that critiques resumes (CVs) and optionally rewrites them in a more professional format.  
It supports a credit-based flow to simulate monetization logic (buy credits / watch ad), and includes a lightweight precheck to prevent non-resume documents from being processed.

## Features

### Analyze
- **Free analysis (0 credits)** when no target job role is provided.
- **Role-based analysis (2 credits)** when a target job role is provided.
- Produces:
  - Primary score (0–100)
  - Short structure note
  - Optional structure score (only for role-based analysis)
  - Issues / quick wins / rewrite recommendation (model output currently shown in the UI)

### Rewrite
- **General rewrite (2 credits)** when no target job role is provided.
- **Role-targeted rewrite (5 credits)** when a target job role is provided.
- Outputs rewritten resume as **Markdown**.

### Guardrails & Precheck
- File required checks (no-op prevention): user is warned if they try to Analyze/Rewrite without uploading a file.
- **Resume/CV precheck** (heuristic):
  - detects resume-like keyword presence (experience, education, skills, etc.)
  - detects presence of email/phone
  - rejects very short or academic-like documents

### File Parsing
- Supports **PDF** (PyPDF2 text extraction) and **TXT**.
- Upload size limit: **5MB**
- Extraction is cached using `st.cache_data` to avoid re-parsing the same file repeatedly.

### Logging
- Logs to `logs/app.log` with rotation (max 1MB, 3 backups).
- Logs OpenAI request start/end + usage tokens (when available).

---
## Setup (Local)

### 1) Install dependencies (uv)
```bash
uv sync
```

### 2) Configure environment variables
Create a .env file in the project root:

```bash
OPENAI_API_KEY=your_key_here
DEBUG=1
```


### 3) Run the app

```bash
uv run streamlit run main.py
```

### Project Structure

```text
app/
├── __init__.py
├── analyzer.py     # OpenAI client call + logging
├── file_parser.py  # PDF/TXT parsing + size limit + cache
├── logger.py       # Rotating file logger
├── precheck.py     # Heuristic resume detection
├── prompts.py      # Prompt builders
└── ui.py           # Streamlit UI + credit flow
logs/               # created at runtime
main.py             # entrypoint (loads .env, runs app)
legacy_main.py      # legacy code kept as comments
pyproject.toml
uv.lock
README.md
```

## Debug mode 

This project has a debug gate controlled by the `DEBUG` environment variable.

- `DEBUG=1` enables debug-only UI blocks:
  - “Debug details” expander (raw exception + traceback)
  - “Raw model output (debug)” expander (full LLM output)

- `DEBUG=0` (or unset) disables these blocks.

Use DEBUG only during local development.

Notes:

- The app expects readable text from the uploaded file (PDF text extraction may vary depending on PDF type).
- Credits are a simulation layer for feature gating and UI flow.
