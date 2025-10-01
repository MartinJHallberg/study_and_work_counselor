# Study & Work Counselor - Makefile

# Default target - run the Streamlit app
start-app:
    poetry run streamlit run app/streamlit_app.py

.PHONY: start-app