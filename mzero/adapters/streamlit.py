"""Streamlit interactive UI component adapter for mzero."""

from mzero.main import RAG


def render_mzero_chat(docs_path: str = "./docs"):
    """Mounts a complete interactive mzero chat interface inside any Streamlit app."""
    try:
        import streamlit as st
    except ImportError:
        raise ImportError("Streamlit is required. Install with: pip install streamlit")

    st.title("mzero AI Knowledge Base")

    if "rag" not in st.session_state:
        st.session_state["rag"] = RAG(docs_path=docs_path)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = st.session_state["rag"].ask(prompt)
                st.markdown(res.answer)

                if res.citations:
                    with st.expander("📚 Sources & Citations"):
                        for cite in res.citations:
                            st.write(f"- **{cite.source_file}**: *\"{cite.snippet}\"*")

        st.session_state.messages.append({"role": "assistant", "content": res.answer})
