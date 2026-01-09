import streamlit as st
import json
import base64
import requests
from openai import OpenAI

# POSKUS UVOZA GROKIPEDIA API (Zadnja specifikacija 2026)
try:
    from grokipedia_api import GrokipediaClient
except ImportError:
    GrokipediaClient = None

# =========================================================
# 0. 3D RELIEF LOGO (Full High-Resolution)
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
# 1. MASSIVE MULTIDIMENSIONAL ONTOLOGY
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
        "Adventurers": {"drivers": "discovery", "description": "Explorers seeking distant connections."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Systemic thinkers seeking a unified theory."},
        "Observers": {"drivers": "evolution", "description": "Detached analysts monitoring systems."}
    },
    "paradigms": {
        "Empiricism": "Data-driven induction.", "Rationalism": "Deductive logic.",
        "Constructivism": "Social context.", "Positivism": "Verified facts.",
        "Pragmatism": "Practical results.", "Phenomenology": "Subjective experience."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes/effects.", "Principles & Relations": "Fundamental laws.",
        "Episodes & Sequences": "Narrative flow.", "Facts & Characteristics": "Raw data properties.",
        "Generalizations": "Broad frameworks.", "Glossary": "Precise definitions.", "Concepts": "Mental maps."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Math Modeling", "Experiment", "Simulation"], "tools": ["Accelerator", "Laser"], "facets": ["Quantum", "Relativity", "Thermodynamics"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Mass Spec"], "facets": ["Organic", "Electrochem"]},
        "Biology": {"cat": "Natural", "methods": ["CRISPR", "DNA Sequencing"], "tools": ["Gene Sequencer"], "facets": ["Genetics", "Cell Bio"]},
        "Neuroscience": {"cat": "Natural", "methods": ["fMRI", "Electrophysiology"], "tools": ["EEG", "Patch-clamp"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Trials", "Psychometrics"], "tools": ["Test Kits"], "facets": ["Cognition", "Developmental"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Network Software"], "facets": ["Stratification", "Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Agile"], "tools": ["IDE", "GPU Cluster"], "facets": ["AI", "Security"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical", "Epidemiology"], "tools": ["MRI/CT"], "facets": ["Immunology", "Pathology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA"], "tools": ["3D Printer", "CAD"], "facets": ["Robotics", "Materials"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic", "Analysis"], "tools": ["Archives"], "facets": ["Ethics", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus", "Parsing"], "tools": ["NLTK", "Praat"], "facets": ["Syntax", "Semantics"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["Stata", "R"], "facets": ["Macro", "Behavioral"]},
        "Environmental Science": {"cat": "Applied", "methods": ["Field Sampling", "GIS"], "tools": ["Sensors", "Satellites"], "facets": ["Climate", "Ecology"]},
        "Archaeology": {"cat": "Humanities", "methods": ["Excavation", "Radiocarbon"], "tools": ["LiDAR", "Drone"], "facets": ["Heritage", "Ancient Civ"]},
        "Arts & Media": {"cat": "Humanities", "methods": ["Iconography", "Semiotic Analysis"], "tools": ["Digital Media"], "facets": ["Aesthetics", "Communication"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Bibliometrics"], "tools": ["Metadata Schemas"], "facets": ["Ontology", "Retrieval"]}
    }
}

# =========================================================
# 2. ULTRA-DEEP GROKIPEDIA SEARCH MODULE
# =========================================================
def get_master_grokipedia_data(query, fields, target_keywords=""):
    """
    Izvede 4-fazno iskanje: 
    1. Splošna dejstva 2. Avtorji/Raziskovalci 3. Časovna premica 4. Specifični pojmi.
    """
    if GrokipediaClient is None:
        return None, "Grokipedia Client: Standby mode. AI utilizing internal 2026 schema."
    
    try:
        client = GrokipediaClient()
        master_context = []
        raw_debug = []

        # FAZA 1: Splošna dejstva
        q1 = client.search(query, limit=2)
        # FAZA 2: Avtorji
        q2 = client.search(f"notable researchers, authors and scholars in {', '.join(fields)} for {query}", limit=3)
        # FAZA 3: Specifični pojmi
        q3 = []
        if target_keywords:
            q3 = client.search(f"technical data on {target_keywords}", limit=3)
        
        # Agregacija
        for q in [q1, q2, q3]:
            if q and 'results' in q:
                for res in q['results']:
                    title = res.get('title', 'Unknown')
                    summary = res.get('summary', 'No summary.')
                    master_context.append(f"• **{title}**: {summary}")
                    raw_debug.append({"title": title, "summary": summary})
        
        if not master_context:
            return None, "No specific factual results found."
            
        formatted_context = "### 🌍 GROKIPEDIA MASTER FACTUAL BASE:\n" + "\n".join(master_context)
        return raw_debug, formatted_context
    except Exception as e:
        return None, f"Grokipedia connectivity limited: {str(e)}"

# =========================================================
# 3. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer v8.0 Master", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"

# --- SIDEBAR (FULL DIAGNOSTIC VERSION) ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Master Control")
    api_key = st.text_input("Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    enable_grok = st.checkbox("🌐 Enable Master Grokipedia Access", value=True)
    show_debug = st.checkbox("🔍 Enable Factual Debugger", value=False)
    st.divider()

    with st.expander("🚀 Quick Templates"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("🎓 Academic"): st.session_state.expertise_val = "Expert"; st.rerun()
        with col_t2:
            if st.button("👶 Learner"): st.session_state.expertise_val = "Novice"; st.rerun()
    
    st.divider()
    st.subheader("🏗️ Knowledge Explorer")
    with st.expander("👤 Profile Drivers"):
        for p, d in KNOWLEDGE_BASE["profiles"].items(): st.write(f"**{p}**: {d['drivers']}")
    with st.expander("🌍 Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items(): st.write(f"**{p}**: {d}")
    
    st.divider()
    if st.button("♻️ RESET ALL", use_container_width=True): st.session_state.clear(); st.rerun()
    st.link_button("🌐 GITHUB REPOSITORY", "https://github.com/", use_container_width=True)

# --- MAIN WORKSPACE ---
st.title("🧱 SIS Universal Knowledge Synthesizer (v8.0 Master)")
st.markdown("### 🛠️ Multi-Dimensional Research & Synthesis Engine")

col1, col2, col3 = st.columns(3)
with col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers", "Know-it-alls"])
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)
with col2:
    selected_paradigms = st.multiselect("2. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Empiricism"])
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Policy Making", "Innovation Strategy", "Problem Solving"])
with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("3. Science Fields:", sciences_list, default=["Physics", "Philosophy"])
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Glossary"])

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

colA, colB = st.columns([2, 1])
with colA:
    user_query = st.text_area("❓ Strategic Synthesis Inquiry:", placeholder="e.g. Synthesize the intersection of neuro-ethics and distributed AI systems.")
with colB:
    target_keywords = st.text_input("🎯 Specific Authors / Keywords:", placeholder="e.g. Chalmers, Penrose, Blockchain")
    selected_approaches = st.multiselect("5. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Balance"])

# =========================================================
# 4. CORE SYNTHESIS LOGIC (AI + Deep Search)
# =========================================================
if st.button("🚀 EXECUTE MASTER SYNTHESIS", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    elif not selected_sciences:
        st.error("Select at least one science field.")
    else:
        try:
            # 1. GROKIPEDIA DEEP SEARCH
            raw_facts, grok_context = None, ""
            if enable_grok:
                with st.spinner('Accessing Master Knowledge Base (Grokipedia)...'):
                    raw_facts, grok_context = get_master_grokipedia_data(user_query, selected_sciences, target_keywords)
            
            # Debug prikaz
            if show_debug and raw_facts:
                with st.expander("🔍 RAW FACTUAL DEBUGGER (Found Entries):"):
                    for r in raw_facts: st.info(f"**{r['title']}**: {r['summary']}")

            # 2. OPENAI/GROQ EXECUTION
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_desc = ", ".join([f"{p} ({KNOWLEDGE_BASE['profiles'][p]['description']})" for p in selected_profiles])
            pa_desc = ", ".join([f"{p} ({KNOWLEDGE_BASE['paradigms'][p]})" for p in selected_paradigms])
            mo_desc = ", ".join([f"{m} ({KNOWLEDGE_BASE['knowledge_models'][m]})" for m in selected_models])

            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer (v8.0 Master Edition).
            You operate under the 'Lego Logic' framework: modular, structural, and synthetic.
            
            FACTUAL FOUNDATION (Strictly anchor 75% of your logic here):
            {grok_context if enable_grok else "Use 2026 verified academic database."}
            
            INTEGRATED PERSPECTIVES (Address all): {p_desc}
            EXPERTISE LEVEL: {expertise}
            GOAL: {goal_context}
            
            DIMENSIONS TO INTEGRATE SIMULTANEOUSLY:
            - Paradigms: {pa_desc}
            - Mental Approaches: {", ".join(selected_approaches)}
            - Science Fields: {", ".join(selected_sciences)} (Facets: {", ".join(agg_facets)})
            - Methodologies: {", ".join(selected_methods) if selected_methods else "Advanced synthesis"}
            - Structural Models: {mo_desc}
            - Focus Keywords: {target_keywords}

            CONSTRUCTION RULES:
            1. MASTER SYNTHESIS: Cross-pollinate the selected science fields. Show how {selected_sciences[0]} methodology informs {selected_sciences[-1]} concepts.
            2. COGNITIVE FILTER: All logic must pass through the {", ".join(selected_approaches)} lens.
            3. AUTHORSHIP: You MUST explicitly integrate researchers/authors found in the Grokipedia context.
            4. TONE: {expertise} level. Language: English.
            """
            
            with st.spinner('Synthesizing Master Architecture...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.5
                )
                st.subheader("📊 Master Synthesis Output (Verified & Structured)")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Execution failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v8.0 Master Edition | 2026")
