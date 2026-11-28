"""📡 Telecom ITSM RAG Chatbot

Embeddings: OpenAI text-embedding-3-small
LLM: DeepSeek (deepseek-chat)
Vector Store: FAISS (faiss-cpu)
Domain: Telecommunications | Sub-domain: IT Service Management (ITSM)
"""
import os
import streamlit as st

from knowledge_base import PAGES, get_full_document_text
from rag_engine import TelecomRAGEngine

# Page Configuration
st.set_page_config(
    page_title="Telecom ITSM RAG Assistant",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for polished Telecom NOC / ITSM appearance
st.markdown(
    """
    <style>
      .main-header {
        background: linear-gradient(135deg, #0b192c 0%, #1e3e62 100%);
        color: #ffffff;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
        border-left: 6px solid #00ADB5;
      }
      .main-header h1 {
        color: #ffffff;
        font-size: 1.85rem;
        margin: 0 0 6px 0;
        font-weight: 700;
      }
      .main-header p {
        color: #d1d5db;
        margin: 0;
        font-size: 0.95rem;
      }
      .metric-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 8px;
      }
      .badge-p1 { background-color: #fee2e2; color: #b91c1c; border: 1px solid #f87171; }
      .badge-p2 { background-color: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }
      .badge-p3 { background-color: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }
      .badge-success { background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }
      .source-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 8px;
      }
      .source-header {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.9rem;
        margin-bottom: 4px;
      }
      .source-body {
        font-size: 0.85rem;
        color: #334155;
        white-space: pre-wrap;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_secret(key: str, default: str = "") -> str:
    """Safely fetch setting from st.secrets or os.environ."""
    try:
        if key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass
    return os.getenv(key, default).strip()


# Resolve API Keys
default_deepseek_key = get_secret("DEEPSEEK_API_KEY") or get_secret("AI_API_KEY")
default_openai_key = get_secret("OPENAI_API_KEY")
default_deepseek_url = get_secret("AI_BASE_URL", "https://api.deepseek.com")
default_deepseek_model = get_secret("AI_MODEL", "deepseek-chat")

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite-in-orbit.png", width=64)
    st.title("Settings & Status")

    st.subheader("🔑 API Credentials")
    deepseek_api_key = st.text_input(
        "DeepSeek API Key (for LLM)",
        value=default_deepseek_key,
        type="password",
        help="Used to generate grounded answers using deepseek-chat",
    )
    openai_api_key = st.text_input(
        "OpenAI API Key (for Embeddings)",
        value=default_openai_key,
        type="password",
        help="Used by text-embedding-3-small to populate the FAISS vector index",
    )

    st.divider()

    st.subheader("⚙️ Architecture Details")
    st.markdown(
        """
        - **Domain**: Telecommunications
        - **Sub-domain**: ITSM & Post-Mortem Analysis
        - **Embedding Model**: `text-embedding-3-small` (1536 dim)
        - **Vector Index**: FAISS (`IndexFlatIP` Cosine)
        - **Chat LLM**: DeepSeek (`deepseek-chat`)
        - **Document Size**: 3 Comprehensive Pages (15 Semantic Chunks)
        """
    )

    if openai_api_key:
        st.success("🟢 OpenAI Embeddings: Active")
    else:
        st.info("ℹ️ Local Vector Fallback Active. Add OpenAI key for text-embedding-3-small.")

    if deepseek_api_key:
        st.success("🟢 DeepSeek LLM: Connected")
    else:
        st.warning("⚠️ DeepSeek Key Missing: Answers won't generate.")

    st.divider()

    st.subheader("💡 Sample Queries")
    sample_queries = [
        "Which P1 incidents affected OCS and what were their root causes?",
        "What caused the 42-minute CDR ingestion delay from MSC-SOUTH?",
        "What preventive actions were recommended for Kafka poison pills?",
        "Why did the promotional data bundle consume the standard balance instead?",
        "What are the SLA restoration targets for P1, P2, and P3 incidents?",
        "What is the procedure for credential rotation in Runbook RB-ITSM-01?",
        "Who is the CEO of Apple?",  # Grounding test: should be refused
    ]

    selected_sample = None
    for q in sample_queries:
        if st.button(q, use_container_width=True, key=f"btn_{hash(q)}"):
            selected_sample = q

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Initialize RAG Engine with Caching
@st.cache_resource(show_spinner="Indexing Telecom ITSM Document with FAISS...")
def load_rag_engine(oai_key: str, ds_key: str, ds_url: str, ds_model: str) -> TelecomRAGEngine:
    return TelecomRAGEngine(
        openai_api_key=oai_key,
        deepseek_api_key=ds_key,
        deepseek_base_url=ds_url,
        deepseek_model=ds_model,
    )


rag_engine = load_rag_engine(
    openai_api_key,
    deepseek_api_key,
    default_deepseek_url,
    default_deepseek_model,
)

# Header Banner
st.markdown(
    """
    <div class="main-header">
      <h1>📡 Telecom ITSM RAG Operations Assistant</h1>
      <p>Grounding-verified intelligence for Telecommunications Incident Management, Core Network Triage, and Post-Mortems.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Main Navigation Tabs
tab_chat, tab_docs, tab_index = st.tabs(["💬 ITSM Chatbot", "📄 Grounding Document Viewer (3 Pages)", "📊 FAISS Index Explorer"])

# TAB 1: Chatbot Interface
with tab_chat:
    st.markdown("Ask technical questions about Telecom incidents, SLAs, root causes, or runbooks. Every answer is strictly grounded in the 3-page document.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I am your **Telecom ITSM Operations Assistant**.\n\n"
                    "I am indexed on your **3-page Telecom ITSM Knowledge Base** using **FAISS** and **OpenAI text-embedding-3-small**, "
                    "powered by **DeepSeek-Chat**.\n\n"
                    "You can ask me about:\n"
                    "- Incident post-mortems (e.g., OCS Diameter timeouts, MSC-SOUTH CDR delays, Kafka consumer lag)\n"
                    "- Priority definitions and SLA restoration targets (P1, P2, P3)\n"
                    "- Operational Runbooks (Credential rotation, Firewall validation, Tariff release rules)\n\n"
                    "Try one of the suggested sample questions in the sidebar or type your query below!"
                ),
                "sources": [],
            }
        ]

    # Render Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("🔍 View Grounding Evidence & Source Chunks (from FAISS)", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(
                            f"""
                            <div class="source-card">
                              <div class="source-header">
                                📌 {src['title']} &nbsp;|&nbsp; 
                                <span class="badge-success">Page {src['page']}</span> &nbsp;
                                <span class="badge-p3">Similarity: {src.get('score', 0):.4f}</span>
                              </div>
                              <div class="source-body">{src['text']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    # Handle Input from Chat input or Sample buttons
    prompt = st.chat_input("Enter your Telecom ITSM question...") or selected_sample

    if prompt:
        # Display user question
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching FAISS vector database and generating grounded answer with DeepSeek..."):
                response_data = rag_engine.answer_query(prompt, top_k=4)
                answer = response_data["answer"]
                sources = response_data.get("retrieved_chunks", [])
                is_grounded = response_data.get("is_grounded", True)
                is_refusal = response_data.get("is_refusal", False)

                if is_refusal:
                    st.warning("🛡️ **Strict Grounding Refusal**: The question falls outside the provided 3-page Telecom ITSM document.")
                elif is_grounded:
                    st.caption("✅ **Grounded Answer**: Verified against retrieved document context.")

                st.markdown(answer)

                if sources:
                    with st.expander("🔍 View Grounding Evidence & Source Chunks (from FAISS)", expanded=True):
                        st.markdown(f"**Embedding Model:** `{response_data.get('embedding_provider', 'FAISS')}`")
                        for src in sources:
                            st.markdown(
                                f"""
                                <div class="source-card">
                                  <div class="source-header">
                                    📌 {src['title']} &nbsp;|&nbsp; 
                                    <span class="badge-success">Page {src['page']}</span> &nbsp;
                                    <span class="badge-p3">Cosine Score: {src.get('score', 0):.4f}</span>
                                  </div>
                                  <div class="source-body">{src['text']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        # Append assistant message to state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })


# TAB 2: Full Document Viewer
with tab_docs:
    st.subheader("📄 Telecom ITSM Reference Document (3 Pages)")
    st.markdown("Inspect the complete hardcoded knowledge base used to index the FAISS database and verify answer grounding.")

    page_tabs = st.tabs([p["title"].split(":")[0] for p in PAGES])
    for tab, page_data in zip(page_tabs, PAGES):
        with tab:
            st.markdown(f"### {page_data['title']}")
            st.code(page_data["content"], language="text")

    st.download_button(
        label="📥 Download Full Document Text (.txt)",
        data=get_full_document_text(),
        file_name="telecom_itsm_knowledge_base.txt",
        mime="text/plain",
        use_container_width=True,
    )


# TAB 3: FAISS Index Explorer
with tab_index:
    st.subheader("📊 FAISS Vector Index Inspection")
    st.markdown("Examine the semantic chunks stored in the FAISS database with their metadata and retrieval scores.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pages", len(PAGES))
    col2.metric("Indexed Chunks", len(rag_engine.chunks))
    col3.metric("Vector Dimension", rag_engine.embeddings.shape[1] if rag_engine.embeddings is not None else 1536)
    col4.metric("Metric Type", "Inner Product (Cosine)")

    st.markdown("#### Indexed Chunks Overview")
    for i, chunk in enumerate(rag_engine.chunks, 1):
        with st.expander(f"Chunk {i}: [{chunk['id']}] {chunk['title']} (Page {chunk['page']})"):
            st.markdown(f"**Category:** `{chunk['category']}` &nbsp;|&nbsp; **Tags:** `{', '.join(chunk['tags'])}`")
            st.text_area("Chunk Content", chunk["text"], height=120, key=f"chunk_txt_{i}")
