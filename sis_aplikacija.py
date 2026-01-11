import streamlit as st
import json
import base64
import requests
from openai import OpenAI
import streamlit.components.v1 as components

# =========================================================
# GOOGLE ANALYTICS INTEGRACIJA
# =========================================================
GA_ID = "G-90E8P7QLF6" 

ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
"""

# =========================================================
# 0. POMOŽNE FUNKCIJE IN LOGO (Embedded SVG)
# =========================================================
def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

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

def fetch_real_academic_data(author_input):
    """Dejanska povezava s Semantic Scholar API za pridobivanje del po imenu ali ORCID."""
    if not author_input: return ""
    results_text = ""
    authors = [a.strip() for a in author_input.split(",")]
    for author in authors:
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{author}\"&limit=5&fields=title,year,abstract,authors,citationCount"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for paper in data:
                    title = paper.get("title", "N/A")
                    year = paper.get("year", "N/A")
                    abstract = paper.get("abstract", "No abstract available.")
                    results_text += f"\n- STUDY: {title} ({year}). ABSTRACT: {abstract[:300]}...\n"
        except: continue
    return results_text

# =========================================================
# 1. THE ADVANCED MULTIDIMENSIONAL ONTOLOGY (POPOLNA)
# =========================================================
KNOWLEDGE_BASE = {
    "mental_approaches": [
        "Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max",
        "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination",
        "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation",
        "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)",
        "Condensation", "Constant", "Associativity"
    ],
    "profiles": {
        "Adventurers": {"drivers": "discovery", "description": "Explorers seeking hidden patterns."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Systemic thinkers seeking absolute clarity."},
        "Observers": {"drivers": "evolution", "description": "Detached analysts of systemic change."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience and induction.",
        "Rationalism": "Knowledge based on deductive logic and innate principles.",
        "Constructivism": "Knowledge as a social and cognitive construction.",
        "Positivism": "Strict adherence to observable and verifiable facts.",
        "Pragmatism": "Knowledge validated by its practical consequences."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing the chain of causes, effects, and the 'why'.",
        "Principles & Relations": "Focusing on constant laws and fundamental correlations.",
        "Episodes & Sequences": "Organizing knowledge as a chronological flow.",
        "Facts & Characteristics": "Focusing on raw data and properties of objects.",
        "Generalizations": "Moving from specific data points to broad frameworks.",
        "Glossary": "Precise definitions of terminology.",
        "Concepts": "Situational conceptual maps and abstract mental constructs."
    },
    "subject_details": {
        "Physics": {
            "cat": "Natural Sciences",
            "methods": ["Mathematical Modeling", "Experimental Method", "Simulation"],
            "tools": ["Particle Accelerator", "Spectrometer", "Interferometer"],
            "facets": ["Quantum Mechanics", "Relativity", "Thermodynamics"]
        },
        "Chemistry": {
            "cat": "Natural Sciences",
            "methods": ["Chemical Synthesis", "Spectroscopy", "Chromatography"],
            "tools": ["Mass Spectrometer", "NMR Spectrometer", "Electron Microscope"],
            "facets": ["Molecular Bonding", "Organic Chemistry", "Electrochemistry"]
        },
        "Biology": {
            "cat": "Natural Sciences",
            "methods": ["CRISPR Editing", "DNA Sequencing", "Field Observation"],
            "tools": ["Gene Sequencer", "Confocal Microscope", "Bio-Incubator"],
            "facets": ["Genetics", "Cell Biology", "Ecology"]
        },
        "Neuroscience": {
            "cat": "Natural Sciences",
            "methods": ["Neuroimaging", "Electrophysiology", "Optogenetics"],
            "tools": ["fMRI Scanner", "EEG", "Patch-clamp Amplifier"],
            "facets": ["Neuroplasticity", "Synaptic Transmission", "Cognitive Mapping"]
        },
        "Psychology": {
            "cat": "Social Sciences",
            "methods": ["Double-Blind Trials", "Psychometrics", "Neuroimaging"],
            "tools": ["fMRI Scanner", "EEG", "Standardized Testing Kits"],
            "facets": ["Behavioral Cognition", "Developmental Psychology"]
        },
        "Sociology": {
            "cat": "Social Sciences",
            "methods": ["Ethnography", "Statistical Surveys", "Content Analysis"],
            "tools": ["Data Analytics Software", "Archival Records", "Network Mapping"],
            "facets": ["Social Stratification", "Group Dynamics", "Urbanization"]
        },
        "Computer Science": {
            "cat": "Formal Sciences",
            "methods": ["Algorithm Design", "Formal Verification", "Agile Development"],
            "tools": ["IDE (VS Code)", "Version Control (Git)", "GPU Clusters"],
            "facets": ["Artificial Intelligence", "Cybersecurity", "Distributed Systems"]
        },
        "Medicine": {
            "cat": "Applied Sciences",
            "methods": ["Clinical Trials", "Epidemiology", "Diagnostic Analysis"],
            "tools": ["MRI/CT Scanners", "Stethoscopes", "Bio-Markers"],
            "facets": ["Pathology", "Immunology", "Pharmacology"]
        },
        "Engineering": {
            "cat": "Applied Sciences",
            "methods": ["Prototyping", "Systems Engineering", "Finite Element Analysis"],
            "tools": ["3D Printers", "CAD Software", "Oscilloscopes"],
            "facets": ["Robotics", "Nanotechnology", "Structural Dynamics"]
        },
        "Library Science": {
            "cat": "Applied Sciences",
            "methods": ["Taxonomic Classification", "Archival Appraisal", "Bibliometrics"],
            "tools": ["OPAC Systems", "Metadata Schemas", "Digital Repositories"],
            "facets": ["Information Retrieval", "Knowledge Organization"]
        },
        "Philosophy": {
            "cat": "Humanities",
            "methods": ["Socratic Method", "Conceptual Analysis", "Phenomenology"],
            "tools": ["Library Archives", "Logic Mapping Tools", "Critical Text Analysis"],
            "facets": ["Ethics", "Metaphysics", "Epistemology"]
        },
        "Linguistics": {
            "cat": "Humanities",
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetics"],
            "tools": ["Praat", "Natural Language Toolkits", "Concordance"],
            "facets": ["Syntax & Morphology", "Sociolinguistics"]
        }
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")
components.html(ga_code, height=0)

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine for **Personalized Knowledge Architecture**.")

# --- SIDEBAR START ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    if col_t1.button("🎓 Academic", use_container_width=True):
        st.session_state.expertise_val = "Expert"
        st.rerun()
    if col_t2.button("👶 Learner", use_container_width=True):
        st.session_state.expertise_val = "Novice"
        st.rerun()

    st.divider()
    st.subheader("📚 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🧠 Mental Approaches"):
        for approach in KNOWLEDGE_BASE["mental_approaches"]: st.write(f"• {approach}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items(): st.write(f"**{p}**: {d}")
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()): st.write(f"• **{s}** ({KNOWLEDGE_BASE['subject_details'][s]['cat']})")
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items(): st.write(f"**{m}**: {d}")
    
    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)

# =========================================================
# 🛠️ CONFIGURE INTERFACE (RESTRUCTURED TO 4 ROWS)
# =========================================================
st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# --- VRSTICA 1: RESEARCH AUTHORS (SREDINA) ---
r1_col1, r1_col2, r1_col3 = st.columns([1, 2, 1])
with r1_col2:
    target_authors = st.text_input("👤 Research Authors (Scholar / ORCID):", placeholder="e.g. Karl Petrič, Samo Kralj, Teodor Petrič")
    st.caption("Direct connectivity for interdisciplinary research synergy analysis.")

# --- VRSTICA 2: USER PROFILES, SCIENCE FIELDS, EXPERTISE LEVEL ---
r2_col1, r2_col2, r2_col3 = st.columns(3)
with r2_col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_col2:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("2. Science Fields:", sciences_list, default=[sciences_list[0]])
with r2_col3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

# --- VRSTICA 3: STRUCTURAL MODELS, SCIENTIFIC PARADIGMS, CONTEXT/GOAL ---
r3_col1, r3_col2, r3_col3 = st.columns(3)
with r3_col1:
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=[list(KNOWLEDGE_BASE["knowledge_models"].keys())[0]])
with r3_col2:
    selected_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with r3_col3:
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"])

# --- VRSTICA 4: MENTAL APPROACHES, METHODOLOGIES, SPECIFIC TOOLS ---
r4_col1, r4_col2, r4_col3 = st.columns(3)
with r4_col1:
    selected_approaches = st.multiselect("7. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=[KNOWLEDGE_BASE["mental_approaches"][0]])

agg_methods = []
agg_tools = []
for s in selected_sciences:
    agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_tools.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

with r4_col2:
    selected_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_methods))))
with r4_col3:
    selected_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tools))))

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Synthesize an interdisciplinary solution for...")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    elif not selected_sciences:
        st.warning("Please select at least one Science Field.")
    else:
        try:
            academic_context = ""
            if target_authors:
                with st.spinner(f'Accessing Academic nodes for {target_authors}...'):
                    academic_context = fetch_real_academic_data(target_authors)

            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. Build a 'Lego Logic' architecture.
            
            RESEARCH DATABASE (Linked metadata):
            {academic_context if academic_context else "Use internal scientific knowledge base."}

            OBJECTIVE:
            Synthesize synergy between: {target_authors} and solve: {user_query}.
            Explain how their combined theories increase efficiency for global problem solving.

            CONFIG:
            Profiles: {", ".join(selected_profiles)} | Expertise: {expertise} | Paradigms: {", ".join(selected_paradigms)}
            Sciences: {", ".join(selected_sciences)} | Models: {", ".join(selected_models)} | Approaches: {", ".join(selected_approaches)}
            """
            
            with st.spinner('Synthesizing research synergy...'):
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
st.caption("SIS Universal Knowledge Synthesizer | v4.9 Global Research Synergy Edition | 2026")
