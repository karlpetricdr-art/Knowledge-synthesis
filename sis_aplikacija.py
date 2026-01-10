import streamlit as st
import json
import base64
from openai import OpenAI
import streamlit.components.v1 as components  # Dodano za Google Analytics
from grokipedia import Grokipedia  # Integracija Grokipedia API

# =========================================================
# GOOGLE ANALYTICS INTEGRACIJA
# =========================================================
# V spodnjo spremenljivko vstavite svoj ID merjenja (Measurement ID)
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
    "mental_approaches": [
        "Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max",
        "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination",
        "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation",
        "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)",
        "Condensation", "Constant", "Associativity"
    ],
    "profiles": {
        "Adventurers": {
            "drivers": "cross-disciplinary exploration / discovery",
            "description": "Explorers seeking to connect distant fields and find hidden patterns."
        },
        "Applicators": {
            "drivers": "practical utility / real-world implementation",
            "description": "Pragmatic minds focused on efficiency, usability, and solving concrete challenges."
        },
        "Know-it-alls": {
            "drivers": "foundational unity / total synthesis",
            "description": "Systemic thinkers seeking a unified theory of everything and absolute logical clarity."
        },
        "Observers": {
            "drivers": "systemic evolution / pattern recognition",
            "description": "Detached analysts who monitor how systems change over time."
        }
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience and data-driven induction.",
        "Rationalism": "Knowledge based on deductive logic and innate intellectual principles.",
        "Constructivism": "Knowledge as a social and cognitive construction based on context.",
        "Positivism": "Strict adherence to observable and scientifically verifiable facts.",
        "Pragmatism": "Knowledge validated by its practical consequences and success."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing the chain of causes, effects, and the 'why' behind phenomena.",
        "Principles & Relations": "Focusing on constant laws and fundamental correlations.",
        "Episodes & Sequences": "Organizing knowledge as a chronological flow and narrative processes.",
        "Facts & Characteristics": "Focusing on raw data and properties of living or inanimate objects.",
        "Generalizations": "Moving from specific data points to broad, universal conceptual frameworks.",
        "Glossary": "Precise definitions of terminology and subject-specific labels.",
        "Concepts": "Situational conceptual maps, categories, and abstract mental constructs."
    },
    "subject_details": {
        "Physics": {
            "cat": "Natural Sciences",
            "methods": ["Mathematical Modeling", "Experimental Method", "Computational Simulation"],
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
            "facets": ["Behavioral Cognition", "Neuroscience", "Developmental Psychology"]
        },
        "Sociology": {
            "cat": "Social Sciences",
            "methods": ["Ethnography", "Statistical Surveys", "Content Analysis"],
            "tools": ["Data Analytics Software", "Archival Records", "Network Mapping Tools"],
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
            "methods": ["Taxonomic Classification", "Archival Appraisal", "Bibliometric Analysis"],
            "tools": ["OPAC Systems", "Metadata Schemas (Dublin Core)", "Digital Repositories"],
            "facets": ["Information Retrieval", "Knowledge Organization", "Digital Preservation"]
        },
        "Philosophy": {
            "cat": "Humanities",
            "methods": ["Socratic Method", "Conceptual Analysis", "Phenomenology"],
            "tools": ["Library Archives", "Logic Mapping Tools", "Critical Text Analysis"],
            "facets": ["Ethics", "Metaphysics", "Epistemology"]
        },
        "Linguistics": {
            "cat": "Humanities",
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetic Transcription"],
            "tools": ["Praat", "Natural Language Toolkits (NLTK)", "Concordance Software"],
            "facets": ["Syntax & Morphology", "Sociolinguistics", "Computational Linguistics"]
        }
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

# Vstavljanje Google Analytics kode takoj za konfiguracijo strani
components.html(ga_code, height=0)

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

# Naslov na vrhu osrednje strani
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine for **Personalized Knowledge Architecture**.")

# --- SIDEBAR START ---
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
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    # Dodano: Stikalo za Grokipedia API
    st.divider()
    st.subheader("🌐 External Knowledge")
    enable_grok = st.checkbox("Enable Grokipedia [all] Enhancement", value=False)
    
    st.divider()

    with st.popover("📖 Lego Building Guide", use_container_width=True):
        st.markdown("""
        ### Synthesis Process:
        1. **Foundation:** Choose your **Paradigms**.
        2. **Bricks:** Select **Sciences**, **Methods**, and **Tools**.
        3. **Building Plan:** Select the **Structural Models**.
        4. **Target View:** Match with your **Profiles**.
        """)

    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🎓 Academic", use_container_width=True):
            st.session_state.expertise_val = "Expert"
            st.rerun()
    with col_t2:
        if st.button("👶 Learner", use_container_width=True):
            st.session_state.expertise_val = "Novice"
            st.rerun()

    st.divider()

    st.subheader("📚 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.write(f"**{p}**: {d['description']}")

    with st.expander("🧠 Mental Approaches"):
        for approach in KNOWLEDGE_BASE["mental_approaches"]:
            st.write(f"• {approach}")

    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items():
            st.write(f"**{p}**: {d}")

    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            d = KNOWLEDGE_BASE["subject_details"][s]
            st.write(f"• **{s}** ({d['cat']})")

    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items():
            st.write(f"**{m}**: {d}")
    
    st.divider()

    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    # Gumbi s povezavami
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)

# --- MAIN SELECTION INTERFACE ---
st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")
col1, col2, col3 = st.columns(3)

with col1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=[list(KNOWLEDGE_BASE["profiles"].keys())[0]])
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

with col2:
    selected_paradigms = st.multiselect("2. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=[list(KNOWLEDGE_BASE["paradigms"].keys())[0]])
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"])

with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect("3. Science Fields:", sciences_list, default=[sciences_list[0]])
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=[list(KNOWLEDGE_BASE["knowledge_models"].keys())[0]])

st.divider()

# Dinamična agregacija metod in orodij glede na izbrane znanosti
agg_methods = []
agg_tools = []
for s in selected_sciences:
    agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_tools.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

# Odstranimo duplikate in sortiramo
agg_methods = sorted(list(set(agg_methods)))
agg_tools = sorted(list(set(agg_tools)))

col4, col5, col6 = st.columns(3)
with col4:
    selected_approaches = st.multiselect("5. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=[KNOWLEDGE_BASE["mental_approaches"][0]])
with col5:
    selected_methods = st.multiselect("6. Methodologies:", agg_methods)
with col6:
    selected_tools = st.multiselect("7. Specific Tools:", agg_tools)

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. Synthesize a perspective on AI ethics.")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI + Grokipedia Integration)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key in the sidebar.")
    elif not selected_sciences:
        st.warning("Please select at least one Science Field.")
    else:
        try:
            # --- INTEGRACIJA GROKIPEDIA ---
            grokipedia_context = ""
            if enable_grok:
                with st.spinner('Searching Grokipedia for deep context...'):
                    try:
                        grok = Grokipedia()
                        # Iskanje po Grokipedii (uporaba 'all' metodologije)
                        search_results = grok.search(user_query)
                        if search_results:
                            # Vzamemo povzetek najbolj relevantnega rezultata
                            grokipedia_context = f"\n\nCONTEXT FROM GROKIPEDIA:\n{search_results[0].summary}"
                    except Exception as ge:
                        st.warning(f"Grokipedia search limited or unavailable: {ge}")

            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # Priprava pluralnih nizov za prompt
            profiles_str = ", ".join(selected_profiles)
            paradigms_str = ", ".join(selected_paradigms)
            sciences_str = ", ".join(selected_sciences)
            models_str = ", ".join(selected_models)
            approaches_str = ", ".join(selected_approaches)
            methods_str = ", ".join(selected_methods) if selected_methods else "general methods"
            tools_str = ", ".join(selected_tools) if selected_tools else "standard tools"
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. You construct knowledge architectures using 'Lego Logic'.
            
            USER ATTRIBUTES:
            - Profiles: {profiles_str}
            - Expertise Level: {expertise}
            - Goal: {goal_context}
            
            DIMENSIONS:
            - Paradigms: {paradigms_str}
            - Mental Approaches: {approaches_str} (Apply all these cognitive lenses simultaneously)
            - Sciences: {sciences_str}
            - Methodologies: {methods_str}
            - Tools: {tools_str}
            - Structural Models: {models_str}

            CONSTRUCTION RULES:
            1. Foundation: Use the selected Paradigms ({paradigms_str}) as the logic base.
            2. Cognitive Lens: Apply the combination of '{approaches_str}' as the primary filter for processing information.
            3. Bricks: Use the selected Sciences ({sciences_str}), their methods, and tools as components.
            4. Plan: Structure the output strictly according to the combined requirements of the selected Structural Models: {models_str}.
            5. Integration: Ensure a high-level synthesis (cross-pollination) between all chosen dimensions.
            6. Tone: Adjust for a {expertise} level. 
            7. Language: English.
            {grokipedia_context}
            """
            
            with st.spinner('Synthesizing complex knowledge structure...'):
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
st.caption("SIS Universal Knowledge Synthesizer | v4.1 Multi-Dimensional Edition | 2026")
