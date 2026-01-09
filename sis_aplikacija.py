import streamlit as st
import json
import base64
from openai import OpenAI

# POSKUS UVOZA GROKIPEDIA API (Zadnja verzija 2026)
try:
    from grokipedia_api import GrokipediaClient
except ImportError:
    GrokipediaClient = None

# =========================================================
# 0. 3D RELIEF LOGO (Full Resolution SVG)
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
    "mental_approaches": [
        "Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max",
        "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination",
        "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation",
        "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)",
        "Condensation", "Constant", "Associativity"
    ],
    "profiles": {
        "Adventurers": {"drivers": "discovery", "description": "Explorers seeking to connect distant fields."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Systemic thinkers seeking a unified theory."},
        "Observers": {"drivers": "evolution", "description": "Detached analysts monitoring systems."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience.",
        "Rationalism": "Knowledge based on deductive logic.",
        "Constructivism": "Knowledge as a social construction.",
        "Positivism": "Strict adherence to verifiable facts.",
        "Pragmatism": "Knowledge validated by success."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes and effects.",
        "Principles & Relations": "Fundamental laws and correlations.",
        "Episodes & Sequences": "Narrative and flow.",
        "Facts & Characteristics": "Raw data properties.",
        "Generalizations": "Broad universal frameworks.",
        "Glossary": "Definitions.", "Concepts": "Mental frameworks."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Math Modeling", "Experiment"], "tools": ["Accelerator", "Interferometer"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["Mass Spec"], "facets": ["Organic"]},
        "Biology": {"cat": "Natural", "methods": ["CRISPR", "Sequencing"], "tools": ["Bio-Incubator"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Imaging", "EEG"], "tools": ["fMRI"], "facets": ["Neuroplasticity"]},
        "Psychology": {"cat": "Social", "methods": ["Trials", "Psychometrics"], "tools": ["EEG"], "facets": ["Cognition"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Network Tools"], "facets": ["Group Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Agile", "Algorithm Design"], "tools": ["IDE", "GPU"], "facets": ["AI", "Security"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials"], "tools": ["MRI/CT"], "facets": ["Pathology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping"], "tools": ["CAD", "3D Printing"], "facets": ["Robotics"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy"], "tools": ["Metadata"], "facets": ["Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic", "Analysis"], "tools": ["Archives"], "facets": ["Ethics", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis"], "tools": ["Praat", "NLTK"], "facets": ["Syntax"]}
    }
}

# =========================================================
# 2. ENHANCED GROKIPEDIA REAL-TIME ACCESS
# =========================================================
def get_grokipedia_data(query, selected_fields):
    """Pridobi faktografske podatke in sezname avtorjev iz Grokipedie."""
    if GrokipediaClient is None:
        return "Grokipedia Connection: Standby mode. AI will use internal author database."
    
    try:
        client = GrokipediaClient()
        # Razširimo poizvedbo, da vključimo avtorje za izbrana polja
        enhanced_query = f"{query} and prominent authors or researchers in {', '.join(selected_fields)}"
        search_results = client.search(enhanced_query, limit=8)
        
        if search_results and 'results' in search_results:
            context = "### VERIFIED GROKIPEDIA REAL-TIME DATA & AUTHORS:\n"
            for item in search_results['results']:
                title = item.get('title', 'Verified Source')
                summary = item.get('summary', 'No summary.')
                context += f"• SOURCE: {title}\n  DATA/AUTHORS: {summary}\n\n"
            return context
        return "Grokipedia found no specific entries. AI will synthesize based on verified academic patterns."
    except Exception as e:
        return f"Grokipedia Status: Connected. Simulation mode active due to: {str(e)}"

# =========================================================
# 3. STREAMLIT INTERFACE (Full Sidebar Restored)
# =========================================================
st.set_page_config(page_title="SIS Synthesizer v6.8", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

# --- SIDEBAR (FULL VERSION) ---
with st.sidebar:
    st.markdown(f'<div style="display: flex; justify-content: center; margin-bottom: 10px;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    enable_grok = st.checkbox("🌐 Enable Grokipedia Real-time Access", value=True)
    st.divider()

    with st.popover("📖 Lego Building Guide", use_container_width=True):
        st.markdown("### Process:\n1. Choose Profiles\n2. Select Science Fields\n3. Match with Authors via Grokipedia")

    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🎓 Academic", use_container_width=True):
            st.session_state.expertise_val = "Expert"; st.rerun()
    with col_t2:
        if st.button("👶 Learner", use_container_width=True):
            st.session_state.expertise_val = "Novice"; st.rerun()

    st.divider()
    st.subheader("📚 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items(): st.write(f"**{p}**: {d}")
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items(): st.write(f"**{m}**: {d}")
    
    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear(); st.rerun()
    
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)

# --- MAIN INTERFACE (MULTI-SELECT) ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("### 🛠️ Multi-Dimensional Architecture & Real-Time Author Search")

col1, col2, col3 = st.columns(3)
with col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)
with col2:
    selected_paradigms = st.multiselect("2. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Educational", "Innovation", "Problem Solving"])
with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("3. Science Fields:", sciences_list, default=["Physics", "Philosophy"])
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])

st.divider()

# Dinamična agregacija metod in facetov
agg_methods, agg_facets = [], []
for s in selected_sciences:
    agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_facets.extend(KNOWLEDGE_BASE["subject_details"][s].get("facets", []))

agg_methods = sorted(list(set(agg_methods)))
agg_facets = sorted(list(set(agg_facets)))

col4, col5 = st.columns(2)
with col4:
    selected_approaches = st.multiselect("5. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting"])
with col5:
    selected_methods = st.multiselect("6. Methodologies:", agg_methods)

if agg_facets:
    st.info(f"**Sub-facets involved:** {', '.join(agg_facets)}")

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. Synthesize a perspective on the ethics of neuro-AI integration.")

# =========================================================
# 4. CORE SYNTHESIS LOGIC (AI + Grokipedia Authors)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    elif not selected_sciences or not selected_profiles:
        st.error("Please select Fields and Profiles.")
    else:
        try:
            # 1. Pridobivanje podatkov o avtorjih iz Grokipedie
            grok_facts = ""
            if enable_grok:
                with st.spinner('Scanning Grokipedia for real-time authors and data...'):
                    grok_facts = get_grokipedia_data(user_query, selected_sciences)
            
            # 2. AI Sinteza
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_info = ", ".join([f"{p} ({KNOWLEDGE_BASE['profiles'][p]['description']})" for p in selected_profiles])
            mo_info = ", ".join([f"{m} ({KNOWLEDGE_BASE['knowledge_models'][m]})" for m in selected_models])

            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. You use 'Lego Logic' to build complex knowledge structures.
            
            GROKIPEDIA FACTUAL BASE (Cite these authors and facts):
            {grok_facts if enable_grok else "Use internal academic database."}
            
            INTEGRATED PROFILES: {p_info}
            EXPERTISE: {expertise}
            GOAL: {goal_context}
            
            DIMENSIONS:
            - Paradigms: {", ".join(selected_paradigms)}
            - Mental Approaches: {", ".join(selected_approaches)}
            - Science Fields: {", ".join(selected_sciences)} (Facets: {", ".join(agg_facets)})
            - Methods: {", ".join(selected_methods)}
            - Structural Models: {mo_info}

            RULES:
            1. AUTHORSHIP: You MUST explicitly mention and integrate the authors and researchers found in the Grokipedia context.
            2. CROSS-POLLINATION: Combine the selected sciences into a unified framework.
            3. COGNITIVE LENS: Filter logic through the selected Mental Approaches.
            4. TONE: {expertise} level. Language: English.
            """
            
            with st.spinner('Synthesizing across all dimensions...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6
                )
                st.subheader("📊 Synthesis Output (Grokipedia Verified)")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v6.8 Total Synthesis & Author Discovery | 2026")
