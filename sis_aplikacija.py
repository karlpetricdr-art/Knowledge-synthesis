import streamlit as st
import json
import base64
from openai import OpenAI

# =========================================================
# 0. 3D RELIEF LOGO (Embedded SVG with Depth & Shadows)
# =========================================================
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/>
        </filter>
        <linearGradient id="pyramidSide" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#bdbdbd;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="treeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#66bb6a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2e7d32;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <rect x="116" y="110" width="8" height="70" rx="2" fill="#5d4037" />
    <circle cx="120" cy="85" r="30" fill="url(#treeGrad)" filter="url(#reliefShadow)" />
    <circle cx="95" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <circle cx="145" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <rect x="70" y="170" width="20" height="12" rx="2" fill="#1565c0" filter="url(#reliefShadow)" />
    <rect x="150" y="170" width="20" height="12" rx="2" fill="#c62828" filter="url(#reliefShadow)" />
    <rect x="110" y="185" width="20" height="12" rx="2" fill="#f9a825" filter="url(#reliefShadow)" />
</svg>
"""

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# =========================================================
# 1. THE ADVANCED MULTIDIMENSIONAL ONTOLOGY
# =========================================================
KNOWLEDGE_BASE = {
    # NOVO: Dimenzija mentalnih pristopov
    "mental_approaches": [
        "Perspective shifting",
        "Induction",
        "Deduction",
        "Hierarchy",
        "Mini-max",
        "Whole and part",
        "Addition and composition",
        "Balance",
        "Abstraction and elimination",
        "Openness and closedness",
        "Bipolarity and dialectics",
        "Framework and foundation",
        "Pleasure and displeasure",
        "Similarity and difference",
        "Core (Attraction & Repulsion)",
        "Condensation",
        "Constant",
        "Associativity"
    ],
    "profiles": {
        "Adventurers": {"drivers": "cross-disciplinary exploration", "description": "Explorers seeking distant connections."},
        "Applicators": {"drivers": "practical utility", "description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"drivers": "foundational unity", "description": "Thinkers seeking unified clarity."},
        "Observers": {"drivers": "systemic evolution", "description": "Analysts of pattern recognition."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience.",
        "Rationalism": "Knowledge based on deductive logic.",
        "Constructivism": "Knowledge as a social and cognitive construction.",
        "Positivism": "Strict adherence to verifiable facts.",
        "Pragmatism": "Knowledge validated by practical consequences."
    },
    "knowledge_models": {
        "Causal Connections": "Chain of causes and effects.",
        "Principles & Relations": "Constant laws and correlations.",
        "Episodes & Sequences": "Chronological flow and narrative.",
        "Facts & Characteristics": "Raw data and properties.",
        "Generalizations": "Broad universal frameworks.",
        "Glossary": "Precise definitions.",
        "Concepts": "Conceptual maps and abstract constructs."
    },
    "subject_details": {
        "Neuroscience": {"cat": "Natural Sciences", "methods": ["Neuroimaging", "Electrophysiology", "Optogenetics"], "tools": ["fMRI Scanner", "EEG", "Patch-clamp Amplifier"]},
        "Physics": {"cat": "Natural Sciences", "methods": ["Mathematical Modeling", "Experimental Method", "Computational Simulation"], "tools": ["Particle Accelerator", "Spectrometer", "Interferometer"]},
        "Chemistry": {"cat": "Natural Sciences", "methods": ["Chemical Synthesis", "Spectroscopy", "Chromatography"], "tools": ["Mass Spectrometer", "NMR Spectrometer", "Electron Microscope"]},
        "Biology": {"cat": "Natural Sciences", "methods": ["CRISPR Editing", "DNA Sequencing", "Field Observation"], "tools": ["Gene Sequencer", "Confocal Microscope", "Bio-Incubator"]},
        "Psychology": {"cat": "Social Sciences", "methods": ["Double-Blind Trials", "Psychometrics", "Neuroimaging"], "tools": ["fMRI Scanner", "EEG", "Standardized Testing Kits"]},
        "Sociology": {"cat": "Social Sciences", "methods": ["Ethnography", "Statistical Surveys", "Content Analysis"], "tools": ["Data Analytics Software", "Archival Records", "Network Mapping Tools"]},
        "Computer Science": {"cat": "Formal Sciences", "methods": ["Algorithm Design", "Formal Verification", "Agile Development"], "tools": ["IDE (VS Code)", "Version Control (Git)", "GPU Clusters"]},
        "Medicine": {"cat": "Applied Sciences", "methods": ["Clinical Trials", "Epidemiology", "Diagnostic Analysis"], "tools": ["MRI/CT Scanners", "Stethoscopes", "Bio-Markers"]},
        "Engineering": {"cat": "Applied Sciences", "methods": ["Prototyping", "Systems Engineering", "Finite Element Analysis"], "tools": ["3D Printers", "CAD Software", "Oscilloscopes"]},
        "Library Science": {"cat": "Applied Sciences", "methods": ["Taxonomic Classification", "Archival Appraisal", "Bibliometric Analysis"], "tools": ["OPAC Systems", "Metadata Schemas", "Digital Repositories"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Conceptual Analysis", "Phenomenology"], "tools": ["Library Archives", "Logic Mapping Tools", "Critical Text Analysis"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetic Transcription"], "tools": ["Praat", "NLTK", "Concordance Software"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine with **Mental Approach Architectures**.")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<div style="display: flex; justify-content: center; margin-bottom: 10px;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    with st.expander("🧠 Mental Approaches Explorer"):
        st.write(", ".join(KNOWLEDGE_BASE["mental_approaches"]))

    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            st.write(f"• **{s}**")

    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN SELECTION ---
st.markdown("### 🛠️ Configure Your Cognitive Build")
col1, col2, col3 = st.columns(3)

with col1:
    selected_profile = st.selectbox("1. User Profile:", list(KNOWLEDGE_BASE["profiles"].keys()))
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

with col2:
    selected_paradigm = st.selectbox("2. Scientific Paradigm:", list(KNOWLEDGE_BASE["paradigms"].keys()))
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"])

with col3:
    selected_science = st.selectbox("3. Science Field:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())))
    selected_model = st.selectbox("4. Structural Model:", list(KNOWLEDGE_BASE["knowledge_models"].keys()))

st.divider()

# VRSTICA 2: Mental Approaches, Methodology in Tools
col4, col5, col6 = st.columns(3)
with col4:
    # MENTAL APPROACH POSTAVLJEN PRED METHODOLOGY
    selected_approach = st.selectbox("5. Mental Approach:", KNOWLEDGE_BASE["mental_approaches"])
with col5:
    selected_method = st.selectbox("6. Methodology:", KNOWLEDGE_BASE["subject_details"][selected_science]["methods"])
with col6:
    selected_tool = st.selectbox("7. Specific Tool:", KNOWLEDGE_BASE["subject_details"][selected_science]["tools"])

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. Synthesize a perspective on AI ethics.")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            p_data = KNOWLEDGE_BASE["profiles"][selected_profile]
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. You construct knowledge architectures using 'Lego Logic'.
            
            USER CONTEXT:
            - Profile: {selected_profile} ({p_data['description']})
            - Expertise: {expertise}
            
            COGNITIVE DIMENSIONS:
            - Paradigm: {selected_paradigm}
            - Mental Approach: {selected_approach} (MANDATORY: Process the logic through this specific lens)
            - Science: {selected_science}
            - Methodology: {selected_method}
            - Tool: {selected_tool}
            - Structural Model: {selected_model}

            CONSTRUCTION RULES:
            1. Use {selected_paradigm} as the logical foundation.
            2. Apply the '{selected_approach}' mental approach as the primary cognitive filter for synthesis.
            3. Structure the output strictly according to the {selected_model} framework.
            4. Adjust complexity for {expertise} level. Language: English.
            """
            
            with st.spinner('Building knowledge structure...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6
                )
                st.subheader("📊 Synthesis Output")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v3.6 Mental Approaches Edition | 2026")
