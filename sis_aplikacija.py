import streamlit as st
import json
import base64
from openai import OpenAI

# =========================================================
# 0. 3D RELIEF LOGO (Embedded SVG with Depth & Shadows)
# =========================================================
# Ohranjen stil z reliefom in črnim robom
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Soft Shadow Filter for Relief Effect -->
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/>
        </filter>
        <!-- Gradients for Depth -->
        <linearGradient id="pyramidSide" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#bdbdbd;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="treeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#66bb6a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2e7d32;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background Relief Circle with Black 3D Border -->
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />

    <!-- 3D Pyramid (Two-tone for depth) -->
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    
    <!-- Tree Trunk -->
    <rect x="116" y="110" width="8" height="70" rx="2" fill="#5d4037" />
    
    <!-- 3D Spheres (Knowledge Nodes) -->
    <circle cx="120" cy="85" r="30" fill="url(#treeGrad)" filter="url(#reliefShadow)" />
    <circle cx="95" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <circle cx="145" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    
    <!-- Floating 'Lego' Knowledge Bricks -->
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
            "description": "Explorers seeking to connect distant fields and find hidden patterns in new territories."
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
            "description": "Detached analysts who monitor how systems change over time without direct intervention."
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
st.set_page_config(page_title="SIS Synthesizer Multi-Dim", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: 
    st.session_state.expertise_val = "Intermediate"

# --- SIDEBAR (CELOTNA KOT PREJ) ---
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
    
    st.divider()

    with st.popover("📖 Lego Building Guide", use_container_width=True):
        st.markdown("""
        ### Synthesis Process:
        1. **Foundation:** Choose your **Paradigms**.
        2. **Bricks:** Select **Sciences**, **Methods**, and **Tools**.
        3. **Building Plan:** Select the **Structural Models**.
        4. **Target View:** Match with your **Profile**.
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
    
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)

# --- GLAVNI VMESNIK (MULTI-SELECT NADGRADNJA) ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine for **Personalized Knowledge Architecture**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

col1, col2, col3 = st.columns(3)

with col1:
    selected_profile = st.selectbox("1. User Profile:", list(KNOWLEDGE_BASE["profiles"].keys()))
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

with col2:
    selected_paradigms = st.multiselect(
        "2. Scientific Paradigms:", 
        list(KNOWLEDGE_BASE["paradigms"].keys()), 
        default=[list(KNOWLEDGE_BASE["paradigms"].keys())[0]]
    )
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"])

with col3:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect(
        "3. Science Fields:", 
        sciences_list, 
        default=[sciences_list[0]]
    )
    selected_models = st.multiselect(
        "4. Structural Models:", 
        list(KNOWLEDGE_BASE["knowledge_models"].keys()), 
        default=[list(KNOWLEDGE_BASE["knowledge_models"].keys())[0]]
    )

st.divider()

# Dinamična agregacija metod in orodij glede na vse izbrane znanosti
aggregated_methods = []
aggregated_tools = []
for s in selected_sciences:
    aggregated_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    aggregated_tools.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

# Odstranimo dvojnike in sortiramo po abecedi
aggregated_methods = sorted(list(set(aggregated_methods)))
aggregated_tools = sorted(list(set(aggregated_tools)))

col4, col5, col6 = st.columns(3)

with col4:
    selected_approaches = st.multiselect(
        "5. Mental Approaches:", 
        KNOWLEDGE_BASE["mental_approaches"], 
        default=[KNOWLEDGE_BASE["mental_approaches"][0]]
    )
with col5:
    selected_methods = st.multiselect("6. Methodologies:", aggregated_methods)
with col6:
    selected_tools = st.multiselect("7. Specific Tools:", aggregated_tools)

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. Synthesize a perspective on AI ethics using the selected dimensions.")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key in the sidebar.")
    elif not selected_sciences:
        st.error("Please select at least one Science Field.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            p_data = KNOWLEDGE_BASE["profiles"][selected_profile]
            
            # Priprava pluralnih opisov za prompt
            paradigms_info = ", ".join([f"{p} ({KNOWLEDGE_BASE['paradigms'][p]})" for p in selected_paradigms])
            models_info = ", ".join([f"{m} ({KNOWLEDGE_BASE['knowledge_models'][m]})" for m in selected_models])
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. You construct knowledge architectures using 'Lego Logic'.
            Your task is to integrate multiple dimensions into a unified response.
            
            USER ATTRIBUTES:
            - Profile: {selected_profile} ({p_data['description']})
            - Expertise Level: {expertise}
            - Goal: {goal_context}
            
            DIMENSIONS TO INTEGRATE SIMULTANEOUSLY:
            - Paradigms: {paradigms_info}
            - Mental Approaches: {", ".join(selected_approaches)} (Apply these lenses collectively)
            - Sciences: {", ".join(selected_sciences)}
            - Methodologies: {", ".join(selected_methods) if selected_methods else "General scientific inquiry"}
            - Tools: {", ".join(selected_tools) if selected_tools else "Standard analytical equipment"}
            - Structural Models: {models_info}

            CONSTRUCTION RULES:
            1. MULTI-DIMENSIONAL INTEGRATION: Do not treat the selected sciences or paradigms in isolation. Cross-pollinate them.
            2. COGNITIVE LENS: Process the entire inquiry through the combined filter of the selected Mental Approaches.
            3. BUILDING PLAN: Structure the output by synthesizing the requirements of all selected Structural Models. 
            4. TONE: Adjust the complexity for a {expertise} level. 
            5. LANGUAGE: English.
            """
            
            with st.spinner('Building complex knowledge structure...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt}, 
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.6
                )
                
                st.subheader("📊 Multi-Dimensional Synthesis Output")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v4.1 Multi-Dimensional Engine | 2026")
