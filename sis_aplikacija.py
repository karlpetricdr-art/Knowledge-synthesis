import streamlit as st
import json
import base64
from openai import OpenAI

# =========================================================
# 0. 3D RELIEF LOGO (Inspiracija po priloženi sliki)
# =========================================================
# Ustvarjena ikona, ki simulira "Drevo znanja" z reliefnim efektom in črnim robom.
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="3" dy="3" stdDeviation="2" flood-color="#000" flood-opacity="0.5"/>
        </filter>
        <linearGradient id="trunkGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#5d4037;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3e2723;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Osnovni krog s 3D črnim robom -->
    <circle cx="120" cy="120" r="110" fill="#ffffff" stroke="#000000" stroke-width="6" filter="url(#reliefShadow)" />
    
    <!-- Ozadje razdeljeno na pol (kot na sliki) -->
    <path d="M120 10 A110 110 0 0 0 120 230 Z" fill="#f5f5f5" /> <!-- Leva siva stran -->
    <path d="M120 10 A110 110 0 0 1 120 230 Z" fill="#e8f5e9" /> <!-- Desna zelena stran -->

    <!-- Deblo drevesa z reliefom -->
    <path d="M110 210 Q120 180 120 120 T130 40" stroke="url(#trunkGrad)" stroke-width="12" fill="none" stroke-linecap="round" filter="url(#reliefShadow)"/>
    <path d="M120 180 Q100 150 80 140" stroke="#5d4037" stroke-width="6" fill="none" stroke-linecap="round" />
    <path d="M120 150 Q140 130 160 120" stroke="#5d4037" stroke-width="6" fill="none" stroke-linecap="round" />

    <!-- Leva stran: Zeleni "oblački" (Humanities/Sciences) -->
    <rect x="50" y="60" width="60" height="25" rx="12" fill="#81c784" filter="url(#reliefShadow)" />
    <rect x="40" y="100" width="70" height="25" rx="12" fill="#66bb6a" filter="url(#reliefShadow)" />
    <rect x="55" y="140" width="55" height="25" rx="12" fill="#4caf50" filter="url(#reliefShadow)" />

    <!-- Desna stran: Barvni vozliči (Math, Physics, Bio) -->
    <circle cx="150" cy="70" r="18" fill="#ef5350" filter="url(#reliefShadow)" /> <!-- Math/Red -->
    <circle cx="170" cy="110" r="20" fill="#42a5f5" filter="url(#reliefShadow)" /> <!-- Physics/Blue -->
    <path d="M140 150 Q160 140 180 160 Q160 180 140 170 Z" fill="#ffa726" filter="url(#reliefShadow)" /> <!-- Bio/Orange -->
    
    <!-- Spodnji labirintni simbol (kot na sliki) -->
    <circle cx="120" cy="195" r="25" fill="#263238" filter="url(#reliefShadow)" />
    <path d="M110 185 L130 185 M110 195 L130 195 M110 205 L130 205" stroke="#00bcd4" stroke-width="2" />
</svg>
"""

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# =========================================================
# 1. THE ADVANCED MULTIDIMENSIONAL ONTOLOGY
# =========================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"description": "Explorers seeking to connect distant fields and find hidden patterns."},
        "Applicators": {"description": "Pragmatic minds focused on efficiency and real-world implementation."},
        "Know-it-alls": {"description": "Systemic thinkers seeking a unified theory and absolute clarity."},
        "Observers": {"description": "Detached analysts who monitor how systems change over time."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience and data.",
        "Rationalism": "Knowledge based on deductive logic and intellectual principles.",
        "Constructivism": "Knowledge as a social and cognitive construction.",
        "Positivism": "Strict adherence to verifiable facts.",
        "Pragmatism": "Knowledge validated by its practical success."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing the 'why' and effects behind phenomena.",
        "Principles & Relations": "Focusing on constant laws and fundamental correlations.",
        "Episodes & Sequences": "Organizing knowledge as chronological narrative processes.",
        "Facts & Characteristics": "Focusing on raw data and properties.",
        "Generalizations": "Moving from specific data to broad conceptual frameworks.",
        "Glossary": "Precise definitions of terminology.",
        "Concepts": "Situational conceptual maps and abstract constructs."
    },
    "subject_details": {
        "Neuroscience": {
            "cat": "Natural Sciences",
            "methods": ["Neuroimaging", "Electrophysiology", "Cognitive Mapping"],
            "tools": ["fMRI Scanner", "EEG", "Neural Networks"],
            "facets": ["Neuroplasticity", "Synaptic Transmission", "Brain Architecture"]
        },
        "Linguistics": {
            "cat": "Humanities",
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetic Transcription"],
            "tools": ["Praat", "NLTK (Python)", "Concordance Software"],
            "facets": ["Syntax", "Semantics", "Sociolinguistics"]
        },
        "Library Science": {
            "cat": "Applied Sciences",
            "methods": ["Taxonomic Classification", "Archival Appraisal", "Bibliometrics"],
            "tools": ["OPAC Systems", "Metadata Schemas", "Digital Repositories"],
            "facets": ["Information Retrieval", "Knowledge Organization", "Archiving"]
        },
        "Physics": {
            "cat": "Natural Sciences",
            "methods": ["Mathematical Modeling", "Experimentation"],
            "tools": ["Spectrometer", "Particle Accelerator"],
            "facets": ["Quantum Mechanics", "Relativity"]
        },
        "Chemistry": {
            "cat": "Natural Sciences",
            "methods": ["Chemical Synthesis", "Spectroscopy"],
            "tools": ["Mass Spectrometer", "NMR"],
            "facets": ["Molecular Bonding", "Organic Chemistry"]
        },
        "Biology": {
            "cat": "Natural Sciences",
            "methods": ["CRISPR", "DNA Sequencing"],
            "tools": ["Microscope", "Sequencer"],
            "facets": ["Genetics", "Ecology"]
        },
        "Psychology": {
            "cat": "Social Sciences",
            "methods": ["Psychometrics", "Clinical Trials"],
            "tools": ["Standardized Tests", "fMRI"],
            "facets": ["Behavioral Cognition", "Developmental Psych"]
        },
        "Sociology": {
            "cat": "Social Sciences",
            "methods": ["Ethnography", "Surveys"],
            "tools": ["Network Mapping", "Statistical Software"],
            "facets": ["Social Stratification", "Urbanization"]
        },
        "Computer Science": {
            "cat": "Formal Sciences",
            "methods": ["Algorithm Design", "Agile"],
            "tools": ["IDE", "GPU Clusters"],
            "facets": ["AI", "Cybersecurity"]
        },
        "Medicine": {
            "cat": "Applied Sciences",
            "methods": ["Clinical Trials", "Diagnostics"],
            "tools": ["MRI", "Bio-Markers"],
            "facets": ["Pathology", "Pharmacology"]
        },
        "Engineering": {
            "cat": "Applied Sciences",
            "methods": ["Prototyping", "FEA"],
            "tools": ["3D Printers", "CAD"],
            "facets": ["Robotics", "Nanotechnology"]
        },
        "Philosophy": {
            "cat": "Humanities",
            "methods": ["Conceptual Analysis", "Phenomenology"],
            "tools": ["Logic Mapping", "Archives"],
            "facets": ["Ethics", "Epistemology"]
        }
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine for **Personalized Knowledge Architecture**.")

with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    st.divider()
    with st.expander("🔬 Science Fields Explorer"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            st.write(f"• **{s}**")

    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN SELECTION INTERFACE ---
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
col4, col5 = st.columns(2)
with col4:
    selected_method = st.selectbox("5. Methodology:", KNOWLEDGE_BASE["subject_details"][selected_science]["methods"])
with col5:
    selected_tool = st.selectbox("6. Specific Tool:", KNOWLEDGE_BASE["subject_details"][selected_science]["tools"])

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. Synthesize a perspective on AI ethics.")

if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            system_prompt = f"Synthesize knowledge for a {selected_profile} profile at {expertise} level using {selected_science} and {selected_paradigm} within the {selected_model} framework."
            
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
st.caption("SIS Universal Knowledge Synthesizer | v3.1 Tree Edition | 2026")
