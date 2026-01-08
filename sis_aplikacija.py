import streamlit as st
import json
import base64
from openai import OpenAI

# =========================================================
# 0. NADGRAJEN 3D RELIEF LOGO (Tree of Knowledge Edition)
# =========================================================
# Ta SVG simulira globino, črn reliefni rob in specifične simbole znanja.
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.6"/>
        </filter>
        <linearGradient id="trunkGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#4e342e;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#26140f;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Glavni krog s poudarjenim črnim 3D robom -->
    <circle cx="120" cy="120" r="110" fill="#ffffff" stroke="#000000" stroke-width="8" filter="url(#reliefShadow)" />
    
    <!-- Razdelitev ozadja (Levo: Humanistika, Desno: Naravoslovje) -->
    <path d="M120 10 A110 110 0 0 0 120 230 Z" fill="#f1f8e9" /> 
    <path d="M120 10 A110 110 0 0 1 120 230 Z" fill="#e3f2fd" />

    <!-- Reliefno Deblo drevesa -->
    <path d="M115 210 Q120 180 120 120 T125 40" stroke="url(#trunkGrad)" stroke-width="12" fill="none" stroke-linecap="round" filter="url(#reliefShadow)"/>

    <!-- SIMBOLI NA VEJAH -->
    <!-- NEUROSCIENCE (Simbol možganov / vijolična) -->
    <circle cx="165" cy="80" r="22" fill="#ce93d8" filter="url(#reliefShadow)" />
    <path d="M160 75 Q165 70 170 75 T175 80" stroke="white" fill="none" stroke-width="2"/>
    
    <!-- LIBRARY SCIENCE (Simbol knjige / modra) -->
    <rect x="145" y="130" width="35" height="25" rx="3" fill="#64b5f6" filter="url(#reliefShadow)" />
    <line x1="150" y1="135" x2="175" y2="135" stroke="white" stroke-width="2"/>
    <line x1="150" y1="145" x2="175" y2="145" stroke="white" stroke-width="2"/>

    <!-- LINGUISTICS (Govorni oblaček / zelena) -->
    <rect x="60" y="90" width="40" height="30" rx="10" fill="#81c784" filter="url(#reliefShadow)" />
    <path d="M90 120 L100 130 L100 120" fill="#81c784" />
    <circle cx="75" cy="105" r="2" fill="white"/>
    <circle cx="80" cy="105" r="2" fill="white"/>
    <circle cx="85" cy="105" r="2" fill="white"/>

    <!-- Spodnji LABIRINT (Algoritmi / črna) -->
    <circle cx="120" cy="190" r="28" fill="#37474f" filter="url(#reliefShadow)" />
    <path d="M110 180 H130 M105 190 H135 M110 200 H130" stroke="#4fc3f7" stroke-width="3" stroke-linecap="round"/>
</svg>
"""

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# =========================================================
# 1. POSODOBLJENA MULTIDIMENZIONALNA ONTOLOGIJA
# =========================================================
KNOWLEDGE_BASE = {
    "subject_details": {
        "🧠 Neuroscience": {
            "cat": "Natural Sciences",
            "methods": ["Neuroimaging (fMRI/EEG)", "Electrophysiology", "Cognitive Mapping"],
            "tools": ["Brain-Computer Interfaces", "Neural Networks", "Patch-clamp"],
            "facets": ["Neuroplasticity", "Synaptic Transmission", "Neural Correlates of Consciousness"]
        },
        "📚 Library Science": {
            "cat": "Applied Sciences",
            "methods": ["Taxonomic Classification", "Archival Appraisal", "Information Retrieval"],
            "tools": ["Metadata Schemas (Dublin Core)", "KOHA Systems", "Digital Repositories"],
            "facets": ["Knowledge Organization", "Bibliometrics", "Preservation Theory"]
        },
        "🗣️ Linguistics": {
            "cat": "Humanities",
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Discourse Analysis"],
            "tools": ["NLTK (Natural Language Toolkit)", "Praat", "Concordance Software"],
            "facets": ["Morphology & Syntax", "Semantics", "Computational Linguistics"]
        },
        "⚛️ Physics": {
            "cat": "Natural Sciences", "methods": ["Mathematical Modeling", "Experimentation"],
            "tools": ["Spectrometer", "Particle Accelerator"], "facets": ["Quantum Mechanics", "Thermodynamics"]
        },
        "🧪 Chemistry": {
            "cat": "Natural Sciences", "methods": ["Synthesis", "Spectroscopy"],
            "tools": ["NMR Spectrometer", "Chromatograph"], "facets": ["Molecular Bonding", "Organic Synthesis"]
        },
        "🧬 Biology": {
            "cat": "Natural Sciences", "methods": ["CRISPR Editing", "DNA Sequencing"],
            "tools": ["Sequencer", "Confocal Microscope"], "facets": ["Genetics", "Ecology"]
        },
        "💻 Computer Science": {
            "cat": "Formal Sciences", "methods": ["Algorithm Design", "Formal Verification"],
            "tools": ["IDE", "GPU Clusters"], "facets": ["AI", "Cybersecurity"]
        },
        "🏛️ Philosophy": {
            "cat": "Humanities", "methods": ["Conceptual Analysis", "Phenomenology"],
            "tools": ["Logic Mapping", "Critical Text Analysis"], "facets": ["Ethics", "Epistemology"]
        },
        "🏥 Medicine": {
            "cat": "Applied Sciences", "methods": ["Clinical Trials", "Diagnostics"],
            "tools": ["MRI", "Stethoscopes"], "facets": ["Immunology", "Pharmacology"]
        }
    },
    "profiles": {
        "Adventurers": {"description": "Explorers seeking to connect distant fields."},
        "Applicators": {"description": "Pragmatic minds focused on utility."},
        "Know-it-alls": {"description": "Systemic thinkers seeking unified theory."},
        "Observers": {"description": "Analysts monitoring systemic evolution."}
    },
    "paradigms": {
        "Empiricism": "Data-driven induction.",
        "Rationalism": "Deductive logic.",
        "Constructivism": "Socially constructed context.",
        "Positivism": "Scientifically verifiable facts.",
        "Pragmatism": "Practical consequences and success."
    },
    "knowledge_models": {
        "Glossary": "Precise definitions and terminology.",
        "Concepts": "Conceptual maps and mental constructs.",
        "Causal Connections": "Analyzing 'why' and effects.",
        "Facts & Characteristics": "Raw data and properties.",
        "Generalizations": "Broad universal frameworks."
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

# Inicializacija seje
if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine with **3D Knowledge Architecture**.")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    st.divider()
    st.subheader("📚 Quick Explore")
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            st.write(f"• {s}")
    
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN INTERFACE ---
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

user_query = st.text_area("❓ Your Inquiry:", placeholder="e.g. Synthesize the impact of AI on human language.")

# =========================================================
# 3. SYNTHESIS EXECUTION
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. 
            User: {selected_profile} (Expertise: {expertise}).
            Foundation: {selected_paradigm}.
            Subject: {selected_science} using {selected_method}.
            Structure: {selected_model}.
            Respond in English.
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
st.caption("SIS Universal Knowledge Synthesizer | v3.2 Relief Tree | 2026")
