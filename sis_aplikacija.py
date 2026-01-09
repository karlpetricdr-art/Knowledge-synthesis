import streamlit as st
import json
import base64
import requests
from openai import OpenAI

# =========================================================
# 0. ROBUSTNI UVOZ IN KONFIGURACIJA GROKIPEDIJE
# =========================================================
GROK_AVAILABLE = False
try:
    from grokipedia_api import GrokipediaClient
    GROK_AVAILABLE = True
except ImportError:
    GROK_AVAILABLE = False

# =========================================================
# 1. 3D RELIEF LOGO (Polna ločljivost za leto 2026)
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
# 2. MASIVNA MULTIDIMENZIONALNA ONTOLOGIJA (16+ področij)
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
        "Adventurers": {"drivers": "discovery", "description": "Explorers seeking distant cross-disciplinary connections."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic minds focused on efficiency and practice."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Systemic thinkers seeking a unified theory of everything."},
        "Observers": {"drivers": "evolution", "description": "Detached analysts monitoring systemic patterns."}
    },
    "paradigms": {
        "Empiricism": "Knowledge from data.", "Rationalism": "Knowledge from logic.",
        "Constructivism": "Social context.", "Positivism": "Verified facts.",
        "Pragmatism": "Practical results.", "Phenomenology": "Experience."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes/effects.", "Principles & Relations": "Laws and constants.",
        "Episodes & Sequences": "Chronological flow.", "Facts & Characteristics": "Raw data properties.",
        "Generalizations": "Broad frameworks.", "Glossary": "Terminology.", "Concepts": "Mental maps."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Math Modeling", "Experiment"], "tools": ["Accelerator"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR"], "facets": ["Molecular"]},
        "Biology": {"cat": "Natural", "methods": ["CRISPR", "Sequencing"], "tools": ["Sequencer"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Imaging", "EEG"], "tools": ["fMRI"], "facets": ["Plasticity"]},
        "Psychology": {"cat": "Social", "methods": ["Trials", "Psychometrics"], "tools": ["Test Kits"], "facets": ["Cognition"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Network Tools"], "facets": ["Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithms", "Formal Verification"], "tools": ["GPU"], "facets": ["AI", "Security"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical", "Epidemiology"], "tools": ["MRI/CT"], "facets": ["Immunology"]},
        "Engineering": {"cat": "Applied", "methods": ["CAD", "FEA"], "tools": ["3D Printer"], "facets": ["Robotics"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["Stata"], "facets": ["Macro", "Behavioral"]},
        "Environmental Science": {"cat": "Applied", "methods": ["GIS", "Sampling"], "tools": ["Satellites"], "facets": ["Climate"]},
        "Archaeology": {"cat": "Humanities", "methods": ["Excavation"], "tools": ["LiDAR"], "facets": ["Ancient Civ"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic", "Analysis"], "tools": ["Archives"], "facets": ["Ethics", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis"], "tools": ["Praat"], "facets": ["Syntax"]},
        "Arts & Media": {"cat": "Humanities", "methods": ["Semiotic Analysis"], "tools": ["Digital Media"], "facets": ["Aesthetics"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy"], "tools": ["Metadata"], "facets": ["Ontology"]}
    }
}

# =========================================================
# 3. NAPREDNI MULTI-PASS GROKIPEDIA SEARCH ENGINE
# =========================================================
def get_cognitive_grokipedia_data(query, fields, keywords=""):
    """
    Izvede poglobljeno iskanje v treh korakih za maksimalno faktografsko globino.
    """
    if not GROK_AVAILABLE:
        return None, "Grokipedia API ni zaznan. Sistem uporablja notranje znanje."
    
    try:
        client = GrokipediaClient()
        combined_context = []
        author_list = []

        # 1. KORAK: Iskanje dejstev
        res_facts = client.search(f"core facts and empirical data about {query}", limit=3)
        # 2. KORAK: Iskanje specifičnih avtorjev in teorij
        res_authors = client.search(f"leading researchers, scholars and specific authors in {', '.join(fields)} regarding {query or keywords}", limit=4)
        # 3. KORAK: Iskanje po ključnih besedah
        res_key = []
        if keywords:
            res_key = client.search(f"detailed scientific analysis of {keywords}", limit=2)

        # Agregacija vseh najdb
        for r_set in [res_facts, res_authors, res_key]:
            if r_set and 'results' in r_set:
                for item in r_set['results']:
                    title = item.get('title', 'Unknown Source')
                    summary = item.get('summary', 'No summary.')
                    combined_context.append(f"SOURCE [{title}]: {summary}")
                    author_list.append(title)

        if not combined_context:
            return None, "Grokipedia za to poizvedbo ni vrnila specifičnih podatkov."

        full_context = "### 📚 GROKIPEDIA KNOWLEDGE ANCHOR (STRICT FIDELITY REQUIRED):\n" + "\n".join(combined_context)
        return author_list, full_context

    except Exception as e:
        return None, f"Napaka pri povezavi z Grokipedijo: {str(e)}"

# =========================================================
# 4. STREAMLIT VMESNIK (v9.0)
# =========================================================
st.set_page_config(page_title="SIS Synthesizer v9.0 Master", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"

# --- SIDEBAR DIAGNOSTIKA ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Master Controller")
    api_key = st.text_input("Groq API Key:", type="password")
    
    st.divider()
    enable_grok = st.checkbox("🌐 Activate Grokipedia Deep-Link", value=True)
    show_raw_grok = st.checkbox("🔍 Debug: Show Grokipedia Context", value=False)
    st.divider()

    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🎓 Academic"): st.session_state.expertise_val = "Expert"; st.rerun()
    with col_t2:
        if st.button("👶 Learner"): st.session_state.expertise_val = "Novice"; st.rerun()
    
    st.divider()
    if st.button("♻️ RESET ALL", use_container_width=True): st.session_state.clear(); st.rerun()
    st.link_button("🌐 GITHUB", "https://github.com/", use_container_width=True)

# --- MAIN WORKSPACE ---
st.title("🧱 SIS Universal Knowledge Synthesizer (v9.0 Master)")
st.markdown("### 🛠️ Strategic Cognitive Architecture & Factual Anchoring")

col1, col2, col3 = st.columns(3)
with col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Know-it-alls", "Adventurers"])
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)
with col2:
    selected_paradigms = st.multiselect("2. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Positivism"])
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making", "Innovation Strategy"])
with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("3. Science Fields:", sciences_list, default=["Physics", "Neuroscience"])
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Principles & Relations"])

st.divider()

# Dinamična agregacija metod in facetov
agg_methods, agg_facets = [], []
for s in selected_sciences:
    agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_facets.extend(KNOWLEDGE_BASE["subject_details"][s]["facets"])

agg_methods = sorted(list(set(agg_methods)))
agg_facets = sorted(list(set(agg_facets)))

colA, colB = st.columns([2, 1])
with colA:
    user_query = st.text_area("❓ Strategic Synthesis Inquiry:", placeholder="e.g. Synthesize the intersection of quantum entropy and neural plasticity.")
with colB:
    target_keywords = st.text_input("🎯 Specific Authors / Keywords:", placeholder="e.g. Penrose, Friston, Kandel")
    selected_approaches = st.multiselect("5. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Hierarchy"])

# =========================================================
# 5. JEDRNA LOGIKA IZVEDBE (Z VOJSKOVANJEM AI)
# =========================================================
if st.button("🚀 EXECUTE MASTER SYNTHESIS", use_container_width=True):
    if not api_key:
        st.error("Prosim, vnesite Groq API ključ v stransko vrstico.")
    else:
        try:
            # 1. FAZA: PRIDOBIVANJE DEJANSTEV IZ GROKIPEDIJE
            grok_authors, grok_context = None, ""
            if enable_grok:
                with st.spinner('Pridobivanje sidrnih dejstev iz Grokipedije...'):
                    grok_authors, grok_context = get_cognitive_grokipedia_data(user_query, selected_sciences, target_keywords)
            
            # Prikaz Debuggerja
            if show_raw_grok and grok_context:
                st.warning("DEBUG: Ta tekst bo poslan AI modelu kot dejstvo:")
                st.code(grok_context)

            # 2. FAZA: AI SINTEZA (Z NAPREDNIM PROMPTOM)
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_desc = ", ".join([f"{p} ({KNOWLEDGE_BASE['profiles'][p]['description']})" for p in selected_profiles])
            pa_desc = ", ".join([f"{p} ({KNOWLEDGE_BASE['paradigms'][p]})" for p in selected_paradigms])

            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer (v9.0 Master Architect).
            Your logic is grounded in 'Lego Logic' and 'Factual Anchoring'.
            
            STRICT REQUIREMENT: You have been provided with a KNOWLEDGE ANCHOR from Grokipedia.
            You MUST prioritize the data, researchers, and authors mentioned in the KNOWLEDGE ANCHOR. 
            Do not provide generic answers. If an author is mentioned in the context, integrate their specific contribution.
            
            KNOWLEDGE ANCHOR:
            {grok_context if grok_context else "No external data. Use internal verified scientific schemas."}
            
            TARGET DIMENSIONS:
            - Integrated Profiles: {p_desc}
            - Expertise Level: {expertise}
            - Paradigms: {pa_desc}
            - Mental Approaches: {", ".join(selected_approaches)}
            - Science Fields: {", ".join(selected_sciences)} (including {", ".join(agg_facets)})
            - Methodologies: {", ".join(agg_methods)}
            - Structural Models: {", ".join(selected_models)}
            - Key Focus: {target_keywords}

            CONSTRUCTION RULES:
            1. ANCHORING: Begin the response by acknowledging the primary authors or data found in the Grokipedia anchor.
            2. CROSS-POLLINATION: Show the synthesis between {", ".join(selected_sciences)}.
            3. COGNITIVE FILTER: Apply the {", ".join(selected_approaches)} lens to all reasoning.
            4. TONE: {expertise} (highly technical and academic).
            """
            
            with st.spinner('Sintetiziranje arhitekture znanja...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.3 # ZELO nizka temperatura za maksimalno natančnost
                )
                
                st.subheader("📊 Master Synthesis Output (Grokipedia Verified)")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Sinteza ni uspela: {str(e)}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v9.0 Factual Anchoring Edition | 2026")
