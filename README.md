# Mini aviation paper research agent

## Overview
The Aviation Research Agent is a retrieval-augmented research assistant designed to generate structured one-page simple drafts grounded in literature provided in the `data\sources` folder. I did this project based on motivation from a lecture on agents on my Foundations of AI course.

**The system:**
- Loads local research papers from data/sources/
- Splits documents into structured chunks
- Retrieves relevant passages for a user query
- Generates a grounded one-page draft
- Exports results to Markdown
- Logs system events for evaluation and traceability

**The project supports both:**
- LLM Mode (Gemini API-based generation)
- Offline Mode (extractive, no API required)

---

### Installation
### 1. Create Virtual Environment
```python -m venv .venv```
```.\.venv\Scripts\activate```
### 2. Install Dependencies
```pip install -r requirements.txt```

---

### Running the System
### LLM Mode (Requires API Key)
Create a `.env` file in the root directory:
```GOOGLE_API_KEY=your_key_here```  

Run:
`python -m app.cli`

### Offline Mode (No API Required)
`python -m app.draft_offline`  
Offline mode just chunks out relevant sections from the local documents. This is it for now :).

---

- .env, .venv, .git, and cache files are excluded.
- Project is fully reproducible via requirements.txt.
- Offline mode ensures evaluation without API dependency.
