import streamlit as st
import json
import base64
import requests
from openai import OpenAI

# =========================================================
# 0. ROBUSTNI UVOZ GROKIPEDIA API
# =========================================================
# Uporabimo try-except, da preprečimo sesutje aplikacije, če knjižnica ni nameščena
GROK_AVAILABLE = False
try:
    from grokipedia_api import GrokipediaClient
    GROK_AVAILABLE = True
except ImportError:
    GROK_AVAILABLE = False

# =========================================================
# 1. 3D RELIEF LOGO (Full High-Resolution SVG)
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
# 2. MASSIVE MULTIDIMENSIONAL ONTOLOGY (16+ Fields)
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
        "Adventurers": {"drivers": "discovery", "description": "Explorers seeking distant field connections."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Systemic thinkers seeking a unified theory."},
        "Observers": {"drivers": "evolution", "description": "Detached analysts monitoring systems."}
    },
    "paradigms": {
        "Empiricism": "Knowledge from sensory data.",
        "Rationalism": "Knowledge from deductive logic.",
        "Constructivism": "Knowledge as a social construct.",
        "Positivism": "Focus on verifiable facts.",
        "Pragmatism": "Focus on practical utility.",
        "Phenomenology": "Focus on conscious experience."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes and effects.",
        "Principles & Relations": "Fundamental laws and constants.",
        "Episodes & Sequences": "Chronological flow and narratives.",
        "Facts & Characteristics": "Raw data and properties.",
        "Generalizations": "Broad universal frameworks.",
        "Glossary": "Precise terminology definitions.",
        "Concepts": "Situational conceptual maps."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Math Modeling", "Experiment"], "tools": ["Accelerator", "Laser"], "facets": ["Quantum", "Relativity", "Entropy"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["Mass Spec", "NMR"], "facets": ["Molecular", "Kinetics"]},
        "Biology": {"cat": "Natural", "methods": ["CRISPR", "Sequencing"], "tools": ["Bio-Incubator"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Imaging", "EEG"], "tools": ["fMRI Scanner"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Trials", "Psychometrics"], "tools": ["Testing Kits"], "facets": ["Cognition", "Behavioral"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics"], "facets": ["Dynamics", "Stratification"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Formal Verification"], "tools": ["GPU Cluster", "IDE"], "facets": ["AI", "Cybersecurity"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT"], "facets": ["Immunology", "Pathology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA"], "tools": ["3D Printer", "CAD"], "facets": ["Robotics", "Materials"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["R/Stata"], "facets": ["Macroeconomics", "Behavioral Econ"]},
        "Environmental Science": {"cat": "Applied", "methods": ["GIS", "Field Sampling"], "tools": ["Sensors", "Satellites"], "facets": ["Climate Change", "Sustainability"]},
        "Archaeology": {"cat": "Humanities", "methods": ["Excavation", "Radiocarbon"], "tools": ["LiDAR", "Drone"], "facets": ["Heritage", "Ancient Civ"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Analysis"], "tools": ["Archives"], "facets": ["Ethics", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Parsing"], "tools": ["NLTK", "Praat"], "facets": ["Syntax", "Semantics"]},
        "Arts & Media": {"cat": "Humanities", "methods": ["Semiotic Analysis", "Iconography"], "tools": ["Digital Media"], "facets": ["Aesthetics", "Communication"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Bibliometrics"], "tools": ["Metadata Schemas"], "facets": ["Ontology", "Retrieval"]}
    }
}

# =========================================================
# 3. MASTER GROKIPEDIA SEARCH LOGIC (Robust)
# =========================================================
def get_master_grokipedia_data(query, fields, target_keywords=""):
    """Varna funkcija za pridobivanje podatkov iz Grokipedie."""
    if not GROK_AVAILABLE:
        return None, "Grokipedia API library not installed. Simulation mode active."
    
    try:
        client = GrokipediaClient()
        master_results = []
        raw_debug_data = []

        # 1. Iskanje po splošni poizvedbi
        q_gen = client.search(query, limit=2)
        # 2. Iskanje po avtorjih za specifična polja
        q_auth = client.search(f"notable researchers and authors in {', '.join(fields)} for {query}", limit=3)
        # 3. Iskanje po specifičnih ključnih besedah
        q_spec = []
        if target_keywords:
            q_spec = client.search(f"detailed scientific data on {target_keywords}", limit=2)
        
        # Zbiranje vseh rezultatov
        for q_res in [q_gen, q_auth, q_spec]:
            if q_res and 'results' in q_res:
                for item in q_res['results']:
                    master_results.append(f"• **{item.get('title')}**: {item.get('summary')}")
                    raw_debug_data.append({"title": item.get('title'), "summary": item.get('summary')})
        
        if not master_results:
            return None, "Grokipedia did not return specific factual entries."
        
        formatted_context = "### 🌍 GROKIPEDIA MASTER FACTUAL BASE:\n" + "\n".join(master_results)
        return raw_debug_data, formatted_context

    except Exception as e:
        return None, f"Grokipedia connectivity error: {str(e)}"

# =========================================================
# 4. STREAMLIT UI SETUP
# =========================================================
st.set_page_config(page_title="SIS Synthesizer v8.5 Master", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"

# --- SIDEBAR DIAGNOSTICS ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Master Control")
    api_key = st.text_input("Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    enable_grok = st.checkbox("🌐 Enable Master Grokipedia Access", value=True)
    show_debug = st.checkbox("🔍 Show Factual Debugger", value=False)
    st.divider()

    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🎓 Academic", use_container_width=True):
            st.session_state.expertise_val = "Expert"; st.rerun()
    with col_t2:
        if st.button("👶 Learner", use_container_width=True):
            st.session_state.expertise_val = "Novice"; st.rerun()
    
    st.divider()
    if st.button("♻️ RESET SESSION", use_container_width=True):
        st.session_state.clear(); st.rerun()
    st.link_button("🌐 GITHUB REPOSITORY", "https://github.com/", use_container_width=True)

# --- MAIN WORKSPACE ---
st.title("🧱 SIS Universal Knowledge Synthesizer (v8.5 Master)")
st.markdown("### 🛠️ Strategic Multi-Dimensional Research & Synthesis Engine")

# SELECTION BLOCK 1
col1, col2, col3 = st.columns(3)
with col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Know-it-alls", "Adventurers"])
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)
with col2:
    selected_paradigms = st.multiselect("2. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Empiricism"])
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making", "Innovation Strategy"])
with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("3. Science Fields:", sciences_list, default=["Physics", "Philosophy"])
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Principles & Relations"])

st.divider()

# Dinamična agregacija (Metode, Orodja, Faceti)
agg_methods, agg_tools, agg_facets = [], [], []
for s in selected_sciences:
    agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_tools.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])
    agg_facets.extend(KNOWLEDGE_BASE["subject_details"][s]["facets"])

agg_methods = sorted(list(set(agg_methods)))
agg_tools = sorted(list(set(agg_tools)))
agg_facets = sorted(list(set(agg_facets)))

# SELECTION BLOCK 2
colA, colB = st.columns([2, 1])
with colA:
    user_query = st.text_area("❓ Strategic Synthesis Inquiry:", placeholder="Analyze the cross-section of neuroscience and ancient philosophy.")
with colB:
    target_keywords = st.text_input("🎯 Specific Authors / Keywords:", placeholder="e.g. Plato, Penrose, Microtubules")
    selected_approaches = st.multiselect("5. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Bipolarity and dialectics"])

# --- DISPLAY FACETS ---
if agg_facets:
    st.info(f"**Available Sub-Facets:** {', '.join(agg_facets)}")

# =========================================================
# 5. EXECUTION LOGIC
# =========================================================
if st.button("🚀 EXECUTE MASTER SYNTHESIS", use_container_width=True):
    if not api_key:
        st.error("Missing API Key. Please provide your Groq API Key in the sidebar.")
    elif not selected_sciences or not selected_profiles:
        st.warning("Please select at least one Science Field and one User Profile.")
    else:
        try:
            # 1. GROKIPEDIA SEARCH
            raw_facts, grok_context = None, ""
            if enable_grok:
                with st.spinner('Accessing Global Factual Database (Grokipedia)...'):
                    raw_facts, grok_context = get_master_grokipedia_data(user_query, selected_sciences, target_keywords)
            
            # Prikaži Debugger
            if show_debug and raw_facts:
                with st.expander("🔍 RAW FACTUAL DEBUGGER (Entries Found)"):
                    for r in raw_facts: st.info(f"**{r['title']}**: {r['summary']}")

            # 2. AI SYNTHESIS (GROQ)
            # Uporabljamo Groq preko OpenAI knjižnice
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_descriptions = ", ".join([f"{p} ({KNOWLEDGE_BASE['profiles'][p]['description']})" for p in selected_profiles])
            pa_descriptions = ", ".join([f"{p} ({KNOWLEDGE_BASE['paradigms'][p]})" for p in selected_paradigms])
            mo_descriptions = ", ".join([f"{m} ({KNOWLEDGE_BASE['knowledge_models'][m]})" for m in selected_models])

            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer (v8.5 Master Architect).
            Your framework is 'Lego Logic': modular, cross-disciplinary, and structural.
            
            FACTUAL FOUNDATION (Anchor 75% of your logic here):
            {grok_context if enable_grok else "Use internal 2026 academic data schemas."}
            
            TARGET DIMENSIONS:
            - Integrated Profiles: {p_descriptions}
            - Paradigms: {pa_descriptions}
            - Mental Approaches: {", ".join(selected_approaches)}
            - Science Fields: {", ".join(selected_sciences)} (Facets: {", ".join(agg_facets)})
            - Methodologies: {", ".join(agg_methods) if agg_methods else "Advanced synthesis"}
            - Structural Models: {mo_descriptions}
            - Focus Target: {target_keywords}

            CONSTRUCTION RULES:
            1. CROSS-POLLINATION: Combine the science fields into a unified technical framework.
            2. COGNITIVE FILTER: Process all logic through the {", ".join(selected_approaches)} lens.
            3. AUTHORSHIP: You MUST explicitly integrate and cite researchers/authors found in the Grokipedia context.
            4. TONE: {expertise} level. Language: English.
            """
            
            with st.spinner('Synthesizing Knowledge Architecture...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.5
                )
                
                st.subheader("📊 Master Synthesis Output")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
            st.info("Check if your Groq API Key is valid and the model name is correct.")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v8.5 Master Architect | 2026")
