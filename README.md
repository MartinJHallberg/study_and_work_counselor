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

### Project Structure

```
app/
├── streamlit_app.py    # Main entry point
├── layout.py          # App layout and structure
├── helpers.py         # Core functionality and utilities
└── controls.py        # UI components and sidebar controls
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
- **Modular Architecture**: Split into layout, helpers, and controls
- **Three-column Layout**: Left navigation, main chat, right step details
- **Chat Interface**: Interactive conversation with the AI agent
- **Profiling Stage**: Collects and refines profile information with progress tracking
- **Job Recommendation Stage**: Generates and displays job matches
- **Profile Snapshot**: Real-time view of collected information
- **Step-specific Guidance**: Contextual tips and information
- **Conversation Reset**: Clear state and start over

### Next Steps / Ideas
- Stream responses token-by-token
- Persist sessions (e.g. to SQLite)
- Add feedback buttons on recommendations
- Export profile + recommendations to PDF/Markdown
