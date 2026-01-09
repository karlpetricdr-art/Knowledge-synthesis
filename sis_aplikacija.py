import streamlit as st
import json
import base64
import requests
from openai import OpenAI

# UVOZ ISKALNIKOV
try:
    from grokipedia_api import GrokipediaClient
    GROK_READY = True
except ImportError:
    GROK_READY = False

try:
    from scholarly import scholarly
    SCHOLAR_READY = True
except ImportError:
    SCHOLAR_READY = False

# =========================================================
# 0. 3D RELIEF LOGO (Full 2026 Master Resolution)
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
# 1. EXTENDED MULTIDIMENSIONAL ONTOLOGY (Master Class)
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
        "Adventurers": {"drivers": "discovery", "description": "Cross-disciplinary explorers."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic efficiency experts."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Unified theory systemic thinkers."},
        "Observers": {"drivers": "evolution", "description": "Systemic pattern monitors."}
    },
    "paradigms": {
        "Empiricism": "Data-driven induction.", "Rationalism": "Logical deduction.",
        "Constructivism": "Social construction.", "Positivism": "Absolute facts.",
        "Pragmatism": "Utility focus.", "Phenomenology": "First-person experience."
    },
    "knowledge_models": {
        "Causal Connections": "Causes/Effects.", "Principles & Relations": "Fundamental laws.",
        "Episodes & Sequences": "Narrative flow.", "Facts & Characteristics": "Raw data.",
        "Generalizations": "Broad frameworks.", "Glossary": "Definitions.", "Concepts": "Mental maps."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Math Modeling", "Experiment"], "tools": ["Accelerator"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis"], "tools": ["Mass Spec"], "facets": ["Organic"]},
        "Biology": {"cat": "Natural", "methods": ["CRISPR"], "tools": ["Sequencer"], "facets": ["Genetics"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Imaging"], "tools": ["fMRI"], "facets": ["Plasticity"]},
        "Psychology": {"cat": "Social", "methods": ["Trials"], "tools": ["Psychometrics"], "facets": ["Behavioral"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography"], "tools": ["Network Tools"], "facets": ["Dynamics"]},
        "Economics": {"cat": "Social", "methods": ["Game Theory", "Econometrics"], "tools": ["Stata"], "facets": ["Macro", "Micro"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic", "Analysis"], "tools": ["Archives"], "facets": ["Ethics", "Ontology"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithms"], "tools": ["GPU"], "facets": ["AI", "Crypto"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical"], "tools": ["MRI/CT"], "facets": ["Genomics"]},
        "History": {"cat": "Humanities", "methods": ["Historiography"], "tools": ["Archives"], "facets": ["Civilizations"]},
        "Engineering": {"cat": "Applied", "methods": ["FEA"], "tools": ["3D Printers"], "facets": ["Robotics"]}
    }
}

# =========================================================
# 2. ACADEMIC RESEARCH ENGINE (Grokipedia + Google Scholar)
# =========================================================
def academic_research_engine(query, fields, keywords=""):
    """
    Sinteza med Grokipedio (fakti) in Google Scholarjem (avtorji in citati).
    """
    academic_dossier = []
    
    # --- DEL 1: GROKIPEDIA ---
    if GROK_READY:
        try:
            g_client = GrokipediaClient()
            g_res = g_client.search(f"{query} {keywords}", limit=3)
            if g_res and 'results' in g_res:
                for r in g_res['results']:
                    academic_dossier.append(f"[GROKIPEDIA FAKT]: {r.get('title')} - {r.get('summary')}")
        except: pass

    # --- DEL 2: GOOGLE UČENJAK (Google Scholar) ---
    if SCHOLAR_READY:
        try:
            # Iščemo avtorje po panogah in ključnih besedah
            scholar_query = f"{keywords} {query} researcher"
            search_query = scholarly.search_pubs(scholar_query)
            
            # Pridobimo prvih 5 akademskih publikacij in njihove avtorje
            for i in range(5):
                pub = next(search_query)
                title = pub['bib']['title']
                authors = ", ".join(pub['bib']['author'])
                year = pub['bib'].get('pub_year', 'N/A')
                venue = pub['bib'].get('venue', 'Academic Journal')
                abstract = pub['bib'].get('abstract', 'No abstract available.')[:300]
                
                academic_dossier.append(f"[GOOGLE SCHOLAR]: Author(s): {authors} ({year}). Paper: '{title}'. Venue: {venue}. Summary: {abstract}...")
        except StopIteration: pass
        except Exception as e:
            academic_dossier.append(f"[SCHOLAR STATUS]: Google Scholar limit reached or error: {str(e)}")

    if not academic_dossier:
        return "No specific academic data found. Relying on master AI internal schemas."
    
    return "### 🎓 ACADEMIC RESEARCH DOSSIER (STRICT FIDELITY):\n" + "\n".join(academic_dossier)

# =========================================================
# 3. STREAMLIT INTERFACE (v11.0 Master)
# =========================================================
st.set_page_config(page_title="SIS Synthesizer v11 Academic", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"

with st.sidebar:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Academic Console")
    api_key = st.text_input("Groq API Key:", type="password")
    
    st.divider()
    enable_scholar = st.checkbox("🌐 Enable Google Učenjak (Scholar)", value=True)
    debug_mode = st.checkbox("🔍 Debug: Show Academic Dossier", value=False)
    st.divider()
    
    if st.button("♻️ Reset Session", use_container_width=True): st.session_state.clear(); st.rerun()
    st.link_button("🌐 GitHub Repo", "https://github.com/", use_container_width=True)

st.title("🧱 SIS Universal Knowledge Synthesizer (v11 Academic)")
st.markdown("### 🎓 Deep Academic Research & Multidimensional Synthesis")

# SELECTION BLOKI
col1, col2, col3 = st.columns(3)
with col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Know-it-alls", "Adventurers"])
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)
with col2:
    selected_paradigms = st.multiselect("2. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Empiricism"])
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Academic Synthesis", "Problem Solving", "Policy Design"])
with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("3. Science Fields:", sciences_list, default=["Physics", "Philosophy"])
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Principles & Relations"])

st.divider()

colA, colB = st.columns([2, 1])
with colA:
    user_query = st.text_area("❓ Academic Synthesis Inquiry:", placeholder="e.g. Synthesize the role of non-locality in quantum mechanics through the lens of analytic philosophy.")
with colB:
    # TO POLJE JE KLJUČNO ZA GOOGLE SCHOLAR
    target_keywords = st.text_input("🎯 Specific Authors / Research Keywords:", placeholder="e.g. Bell, Aspect, David Chalmers")
    selected_approaches = st.multiselect("5. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Induction"])

# =========================================================
# 4. EXECUTION LOGIC
# =========================================================
if st.button("🚀 EXECUTE ACADEMIC SYNTHESIS", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    else:
        try:
            # 1. PRIDOBIVANJE AKADEMSKIH PODATKOV
            academic_dossier = ""
            if enable_scholar:
                with st.spinner('Scouring Google Scholar & Grokipedia for peer-reviewed data...'):
                    academic_dossier = academic_research_engine(user_query, selected_sciences, target_keywords)
            
            if debug_mode and academic_dossier:
                st.info(academic_dossier)

            # 2. AI SINTEZA
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer v11 (Academic Edition).
            You synthesize high-level scientific information using 'Lego Logic'.
            
            ACADEMIC RESEARCH DOSSIER (MANDATORY FIDELITY):
            {academic_dossier if enable_scholar else "Use academic internal patterns."}
            
            DIMENSIONS:
            - Profiles: {", ".join(selected_profiles)}
            - Paradigms: {", ".join(selected_paradigms)}
            - Mental Approaches: {", ".join(selected_approaches)}
            - Science Fields: {", ".join(selected_sciences)}
            - Structural Models: {", ".join(selected_models)}
            - Target Authors/Keywords: {target_keywords}

            CONSTRUCTION RULES:
            1. PEER-REVIEWED FOCUS: You MUST explicitly integrate and cite the authors, papers, and years found in the Academic Research Dossier.
            2. SYNTHETIC DEPTH: Show how {", ".join(selected_sciences)} interlock at a foundational level.
            3. FIDELITY: Do not provide generic AI filler. Use the specific names from Google Scholar (e.g., '{target_keywords}').
            4. TONE: {expertise} (highly formal, academic, and rigorous). Language: English.
            """
            
            with st.spinner('Building Academic Architecture...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.3
                )
                
                st.subheader("📊 Academic Synthesis Output (Scholar Verified)")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v11.0 Google Scholar Integrated | 2026")
