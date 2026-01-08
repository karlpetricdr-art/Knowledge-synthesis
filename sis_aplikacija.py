import streamlit as st
import json
from openai import OpenAI

# =========================================================
# 1. THE ADVANCED MULTIDIMENSIONAL ONTOLOGY
# =========================================================
KNOWLEDGE_BASE = {
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
        "Philosophy": {
            "cat": "Humanities",
            "methods": ["Socratic Method", "Conceptual Analysis", "Phenomenology"],
            "tools": ["Library Archives", "Logic Mapping Tools", "Critical Text Analysis"],
            "facets": ["Ethics", "Metaphysics", "Epistemology"]
        }
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

# Initialize Session State
if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Precision synthesis engine for **Personalized Knowledge Architecture**.")

# --- SIDEBAR START ---
with st.sidebar:
    # OPTIMIZED IMAGE SIZE: Added fixed width to prevent the icon from being too large
    st.image("input_file_2.jpeg", width=250)
    st.header("⚙️ Control Panel")
    
    api_key = st.text_input("Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()

    # Quick Guide
    with st.popover("📖 Lego Building Guide", use_container_width=True):
        st.markdown("""
        ### Synthesis Process:
        1. **Foundation:** Choose your **Paradigm**.
        2. **Bricks:** Select **Science**, **Method**, and **Tool**.
        3. **Building Plan:** Select the **Structural Model** (Glossary, Causal, etc.).
        4. **Target View:** Match with your **Profile**.
        """)

    # Quick Mode Buttons
    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🎓 Academic", use_container_width=True):
            st.session_state.expertise_val = "Expert"
    with col_t2:
        if st.button("👶 Learner", use_container_width=True):
            st.session_state.expertise_val = "Novice"

    st.divider()

    # --- ENHANCED SIDEBAR EXPLORER ---
    st.subheader("📚 Knowledge Explorer")
    
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.write(f"**{p}**: {d['description']}")

    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items():
            st.write(f"**{p}**: {d}")

    with st.expander("🔬 Science Fields"):
        for s, d in KNOWLEDGE_BASE["subject_details"].items():
            st.write(f"• **{s}** ({d['cat']})")

    with st.expander("🛠️ Methodologies"):
        all_methods = sorted(list(set([m for s in KNOWLEDGE_BASE["subject_details"].values() for m in s["methods"]])))
        for m in all_methods:
            st.write(f"• {m}")

    with st.expander("🔧 Specific Tools"):
        all_tools = sorted(list(set([t for s in KNOWLEDGE_BASE["subject_details"].values() for t in s["tools"]])))
        for t in all_tools:
            st.write(f"• {t}")

    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items():
            st.write(f"**{m}**: {d}")
    
    st.divider()

    # Utilities
    if st.button("♻️ Reset Session", use_container_width=True):
        st.rerun()
    
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)

# --- SIDEBAR END ---

# MAIN SELECTION INTERFACE
st.markdown("### 🛠️ Configure Your Cognitive Build")
col1, col2, col3 = st.columns(3)

with col1:
    selected_profile = st.selectbox("1. User Profile:", list(KNOWLEDGE_BASE["profiles"].keys()))
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

with col2:
    selected_paradigm = st.selectbox("2. Scientific Paradigm:", list(KNOWLEDGE_BASE["paradigms"].keys()))
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"])

with col3:
    selected_science = st.selectbox("3. Science Field:", list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_model = st.selectbox("4. Structural Model:", list(KNOWLEDGE_BASE["knowledge_models"].keys()))

st.divider()

col4, col5 = st.columns(2)
with col4:
    # Dynamically filter methods based on science
    selected_method = st.selectbox("5. Methodology:", KNOWLEDGE_BASE["subject_details"][selected_science]["methods"])
with col5:
    # Dynamically filter tools based on science
    selected_tool = st.selectbox("6. Specific Tool:", KNOWLEDGE_BASE["subject_details"][selected_science]["tools"])

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. Synthesize the relationship between entropy and information theory.")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key in the sidebar.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_data = KNOWLEDGE_BASE["profiles"][selected_profile]
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. You construct knowledge architectures using 'Lego Logic'.
            
            USER ATTRIBUTES:
            - Profile: {selected_profile} ({p_data['description']})
            - Expertise Level: {expertise}
            - Goal: {goal_context}
            
            DIMENSIONS:
            - Paradigm: {selected_paradigm} ({KNOWLEDGE_BASE['paradigms'][selected_paradigm]})
            - Science: {selected_science}
            - Methodology: {selected_method}
            - Tool: {selected_tool}
            - Structural Model: {selected_model} ({KNOWLEDGE_BASE['knowledge_models'][selected_model]})

            CONSTRUCTION RULES:
            1. Use the Paradigm as the foundational logic.
            2. Science and Tool are your primary bricks.
            3. Apply the Structural Model as the architectural plan. If 'Glossary', focus on terminology. If 'Concepts', focus on mental maps.
            4. Adjust depth for a {expertise} level.
            5. Response must be in English.
            """
            
            with st.spinner('Assembling knowledge blocks...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.6
                )
                
                st.subheader("📊 Synthesis Output")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | Powered by Groq AI | 2026")
