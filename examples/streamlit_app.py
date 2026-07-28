"""Streamlit interactive UI app example for mzero."""

from mzero.adapters.streamlit import render_mzero_chat

# Renders a complete interactive RAG UI in Streamlit with 1 line of code!
if __name__ == "__main__":
    render_mzero_chat(docs_path="./sample_docs")
