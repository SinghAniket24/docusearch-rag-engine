import streamlit as st
import requests
import uuid
from pypdf import PdfReader

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="DocuSearch Analytics Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "history_stack" not in st.session_state:
    st.session_state["history_stack"] = []

if "latest_metrics" not in st.session_state:
    st.session_state["latest_metrics"] = {}

st.markdown("""
    <style>
    .stApp {
        background-color: #0B132B !important;
        color: #FFFFFF !important;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: #FFFFFF !important;
    }
    .main .block-container {
        padding-top: 1.5rem !important;
    }
    #MainMenu, header[data-testid="stHeader"] .stDeployButton, footer {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #1C2541 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    button[data-testid="sidebar-toggle"] svg, button[aria-label="Collapse sidebar"] svg {
        fill: #00B4D8 !important;
        color: #00B4D8 !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        color: #FFFFFF !important;
        background-color: #0F172A !important;
        border: 2px solid #3A506B !important;
        font-size: 1rem !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] input:focus, div[data-baseweb="textarea"] textarea:focus {
        border-color: #00B4D8 !important;
    }
    div[data-baseweb="input"] input::placeholder, div[data-baseweb="textarea"] textarea::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    div[data-testid="stFileUploader"] section {
        background-color: #0F172A !important;
        border: 2px dashed #3A506B !important;
        border-radius: 6px !important;
    }
    div[data-testid="stFileUploader"] section small {
        color: #94A3B8 !important;
    }
    div.stButton > button {
        color: #FFFFFF !important;
        background-color: #1E293B !important;
        border: 2px solid #3A506B !important;
        font-weight: 700 !important;
        height: 44px !important;
        width: 100% !important;
        border-radius: 6px !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #3A506B !important;
        border-color: #5BC0BE !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #00B4D8 !important;
        color: #0B132B !important;
        border-color: #00B4D8 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #5BC0BE !important;
        color: #0B132B !important;
        border-color: #5BC0BE !important;
    }
    .app-title {
        color: #00B4D8;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.25rem;
    }
    .synthesis-card {
        background-color: #1C2541;
        border: 1px solid #3A506B;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .citation-badge {
        background-color: #0F172A;
        color: #5BC0BE;
        border: 1px solid #3A506B;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-top: 10px;
    }
    .metric-panel {
        background-color: #1C2541;
        border: 1px solid #3A506B;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .panel-header {
        color: #5BC0BE; 
        font-size: 0.85rem; 
        font-weight: 700; 
        letter-spacing: 0.05em;
    }
    .panel-value {
        font-size: 1.35rem; 
        font-weight: 700; 
        color: #FFFFFF; 
        margin-top: 0.25rem;
    }
    
    /* Expander Container Theme Adjustments */
    .stExpander {
        background-color: #1C2541 !important;
        border: 1px solid #3A506B !important;
        border-radius: 6px !important;
        margin-bottom: 1.5rem !important;
    }
    .stExpander details summary {
        color: #00B4D8 !important;
        font-weight: 700 !important;
    }
    
    .step-card {
        background-color: #0F172A;
        border: 1px solid #3A506B;
        padding: 1rem;
        border-radius: 6px;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='app-title'>DocuSearch RAG Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #5BC0BE; margin-top:-5px; font-weight:600;'>Document Intelligence Hub & Search Pipeline</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #3A506B; margin-top: 0; margin-bottom: 1rem; border-width: 2px;'/>", unsafe_allow_html=True)

with st.expander("ℹ️ How it works?", expanded=True):
    st.markdown("""
        <p style="margin: 0; font-size: 1.05rem; color: #E2E8F0; line-height: 1.6;">
            When you upload a document, it is broken down into clean sentence blocks and stored in <strong>ChromaDB (Vector Database)</strong> as high-dimensional mathematical coordinates. When you ask a question, the system uses a dense semantic search to find the exact sentence match based on conceptual meaning rather than raw keywords. This retrieved fact is then injected directly into the <strong>Gemini LLM</strong> context window, allowing the model to synthesize a precise, natural response that is strictly anchored to the source text and stamped with a verifiable page citation.
        </p>
    """, unsafe_allow_html=True)

arch_col1, arch_col2, arch_col3 = st.columns(3)
with arch_col1:
    st.markdown("""
    <div class="step-card">
        <span style="color: #00B4D8; font-weight: 800; font-size: 0.85rem; letter-spacing: 0.05em;">STEP 1</span>
        <p style="color: #FFFFFF; font-weight: 700; margin: 4px 0 2px 0; font-size: 1rem;">Upload Documents</p>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0; line-height: 1.4;">Provide files or text blocks in the sidebar to segment documents into searchable vector units.</p>
    </div>
    """, unsafe_allow_html=True)
with arch_col2:
    st.markdown("""
    <div class="step-card">
        <span style="color: #5BC0BE; font-weight: 800; font-size: 0.85rem; letter-spacing: 0.05em;">STEP 2</span>
        <p style="color: #FFFFFF; font-weight: 700; margin: 4px 0 2px 0; font-size: 1rem;">Ask Questions</p>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0; line-height: 1.4;">Submit queries below. Vague follow-ups automatically adapt using conversation history context.</p>
    </div>
    """, unsafe_allow_html=True)
with arch_col3:
    st.markdown("""
    <div class="step-card">
        <span style="color: #00B4D8; font-weight: 800; font-size: 0.85rem; letter-spacing: 0.05em;">STEP 3</span>
        <p style="color: #FFFFFF; font-weight: 700; margin: 4px 0 2px 0; font-size: 1rem;">Verify Citations</p>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0; line-height: 1.4;">Review targeted answers mapped directly to source records, exact page coordinates, and metrics.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #00B4D8; font-weight:800; font-size:1.6rem; margin-top:0;'>Knowledge Ingestion</h2>", unsafe_allow_html=True)
    
    doc_id = st.text_input("Document ID", placeholder="e.g., policy_manual_2026")
    category = st.text_input("Category Tag", placeholder="e.g., hr_compliance")
    ingest_method = st.radio("Source Type", ["File Upload", "Manual Input"])
    
    pages_payload = []
    
    if ingest_method == "File Upload":
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".txt"):
                raw_text = uploaded_file.read().decode("utf-8")
                pages_payload.append({"page_number": 1, "text": raw_text})
            elif uploaded_file.name.endswith(".pdf"):
                try:
                    pdf_reader = PdfReader(uploaded_file)
                    for idx, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            pages_payload.append({"page_number": idx + 1, "text": page_text})
                except Exception as e:
                    st.error(f"Failed to parse PDF: {e}")
    else:
        raw_text = st.text_area("Text Content", placeholder="Paste reference text here...", height=250)
        if raw_text.strip():
            pages_payload.append({"page_number": 1, "text": raw_text})

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Index Document", use_container_width=True):
        if doc_id and category and pages_payload:
            payload = {
                "id": doc_id,
                "category": category,
                "pages": pages_payload
            }
            try:
                response = requests.post(f"{FASTAPI_URL}/ingest", json=payload)
                if response.status_code == 201:
                    st.sidebar.success(f"Successfully indexed {response.json().get('total_sentences_indexed')} sentence blocks.")
                else:
                    st.sidebar.error(f"Ingestion failed: {response.json().get('detail')}")
            except Exception:
                st.sidebar.error("Backend server is unreachable.")
        else:
            st.sidebar.warning("Please fill in all layout fields.")

col_left, col_right = st.columns([2.2, 1])

with col_left:
    st.markdown("<h3 style='color: #00B4D8; font-weight:700; font-size:1.4rem; margin-top:0;'>Ask the Engine</h3>", unsafe_allow_html=True)
    
    with st.form(key="query_submission_form", clear_on_submit=True):
        user_question = st.text_input("Enter your question", placeholder="Type a question or a follow-up statement...", label_visibility="collapsed")
        
        btn_col1, btn_col2 = st.columns([1.5, 1])
        with btn_col1:
            submit_query = st.form_submit_button(label="Ask Question", type="primary", use_container_width=True)
        with btn_col2:
            clear_chat = st.form_submit_button(label="Clear History", use_container_width=True)
            
    if clear_chat:
        st.session_state["history_stack"] = []
        st.session_state["latest_metrics"] = {}
        st.session_state["session_id"] = str(uuid.uuid4())
        st.rerun()
        
    if submit_query:
        if user_question:
            with st.spinner("Searching knowledge base..."):
                try:
                    payload = {
                        "question": user_question,
                        "session_id": st.session_state["session_id"]
                    }
                    response = requests.post(f"{FASTAPI_URL}/ask", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "gemini_generated_answer" in data:
                            st.session_state["history_stack"].insert(0, {
                                "question": user_question,
                                "answer": data["gemini_generated_answer"],
                                "source": data.get("source_document", "N/A"),
                                "page": data.get("source_page", "N/A")
                            })
                            st.session_state["latest_metrics"] = {
                                "distance_score": data.get("distance_score"),
                                "local_retrieved_fact": data.get("local_retrieved_fact")
                            }
                        else:
                            st.info(data.get("answer", "No direct context match found."))
                    else:
                        st.error(f"Server error: {response.json().get('detail')}")
                except Exception:
                    st.error("Backend server is unreachable.")
        else:
            st.warning("Please enter a question.")

    for exchange in st.session_state["history_stack"]:
        st.markdown(f"""
        <div class="synthesis-card">
            <p style='margin-top:0; color:#5BC0BE; font-weight:700; font-size:0.95rem;'>Q: {exchange['question']}</p>
            <h4 style='margin-top:8px; margin-bottom:4px; color:#00B4D8; font-weight:800; font-size:1.2rem;'>Answer</h4>
            <p style='font-size:1.1rem; line-height:1.6; color:#FFFFFF; margin-bottom:4px;'>{exchange['answer']}</p>
            <div class="citation-badge">📌 Source: {exchange['source']} | Page: {exchange['page']}</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("<h3 style='color: #00B4D8; font-weight:700; font-size:1.4rem; margin-top:0;'>Search Metrics</h3>", unsafe_allow_html=True)
    metrics = st.session_state["latest_metrics"]
    
    if metrics:
        dist = metrics["distance_score"]
        status_indicator = "<span style='color: #22C55E; font-weight:800;'>High Confidence</span>" if dist < 0.8 else "<span style='color: #EAB308; font-weight:800;'>Medium Confidence</span>" if dist <= 1.2 else "<span style='color: #EF4444; font-weight:800;'>Low Confidence</span>"
        
        st.markdown(f"""
        <div class="metric-panel">
            <div class="panel-header">MATCH QUALITY</div>
            <div class="panel-value">{status_indicator}</div>
        </div>
        <div class="metric-panel">
            <div class="panel-header">VECTOR DISTANCE SCORE</div>
            <div class="panel-value" style="font-family: monospace;">{dist}</div>
        </div>
        <div class="metric-panel">
            <div class="panel-header">RETRIEVED SOURCE TEXT</div>
            <p style="font-size: 1rem; color: #E2E8F0; margin-top: 8px; line-height: 1.5; font-style: italic;">"{metrics['local_retrieved_fact']}"</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #94A3B8; font-style: italic;'>Run a query to display real-time pipeline tracking metrics.</p>", unsafe_allow_html=True)