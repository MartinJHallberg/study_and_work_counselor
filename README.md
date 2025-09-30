## Study & Work Counselor

Interactive counselor that profiles a user and recommends job roles using a LangGraph workflow.

### Setup

1. Install dependencies:
```
poetry install
```

2. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Running the CLI (original)
```
poetry run python src/main.py
```

### Streamlit App
```
poetry run streamlit run app/streamlit_app.py
```

Features:
- Chat interface
- Profiling stage (collects and refines profile information)
- Job recommendation stage (after profiling completes or forced via sidebar)
- Sidebar snapshot of extracted profile fields
- Ability to reset conversation/state

### Next Steps / Ideas
- Stream responses token-by-token
- Persist sessions (e.g. to SQLite)
- Add feedback buttons on recommendations
- Export profile + recommendations to PDF/Markdown
