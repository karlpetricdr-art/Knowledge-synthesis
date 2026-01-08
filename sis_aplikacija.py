import streamlit as st
import json
from openai import OpenAI

# =========================================================
# 1. THE MULTIDIMENSIONAL LEGO ONTOLOGY
# =========================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"drivers": "exploration / discovery", "description": "Explorers of new frontiers and hidden patterns."},
        "Applicators": {"drivers": "utility / results", "description": "Practical minds focused on 'how to make it work'."},
        "Know-it-alls": {"drivers": "total synthesis", "description": "Seekers of a unified theory and absolute clarity."},
        "Observers": {"drivers": "detached analysis", "description": "Quiet analysts focused on system evolution and patterns."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience and evidence-based data.",
        "Rationalism": "Knowledge based on reason, logic, and innate intellectual structures.",
        "Constructivism": "Knowledge as a subjective construction of reality and social interaction.",
        "Positivism": "Knowledge strictly based on observable, verifiable, and measurable facts.",
        "Pragmatism": "Knowledge validated by its practical consequences and problem-solving utility."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes, effects, and the 'why' behind phenomena.",
        "Principles & Relations": "Focusing on fundamental laws, correlations, and constant relationships.",
        "Episodes & Sequences": "Structuring knowledge as a flow of events, time sequences, and processes.",
        "Facts & Characteristics": "Focusing on raw data, properties of things, and specific observations.",
        "Generalizations": "Moving from specific locations/materials to broad conceptual frameworks.",
        "Glossary & Concepts": "Establishing clear definitions, labels, and conceptual vocabularies."
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
            "tools": ["Integrated Development Environments (IDE)", "Version Control (Git)", "GPU Clusters"],
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
# 2. STREAMLIT INTERFACE (Advanced Layout)
# =========================================================
st.set_page_config(page_title="SIS Epistemic Synthesizer", page_icon="🧱", layout="wide")

st.title("🧱 SIS - Universal Epistemic Synthesizer")
st.markdown("A multidimensional engine for **Knowledge Architecture** based on your Lego Taxonomy.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    st.subheader("📚 Knowledge Explorer")
    show_db = st.toggle("Enable Explorer Mode", help="Browse all scientific dimensions.")
    
    if show_db:
        with st.expander("👤 Profiles"):
            for p, d in KNOWLEDGE_BASE["profiles"].items():
                st.write(f"**{p}**: {d['description']}")
        with st.expander("🌍 Paradigms"):
            for p, d in KNOWLEDGE_BASE["paradigms"].items():
                st.write(f"**{p}**: {d}")
        with st.expander("🏗️ Structural Models"):
            for m, d in KNOWLEDGE_BASE["knowledge_models"].items():
                st.write(f"**{m}**: {d}")
        with st.expander("🔬 Sciences & Tools"):
            for s, d in KNOWLEDGE_BASE["subject_details"].items():
                st.caption(f"{s}: {', '.join(d['tools'])}")

# MAIN SELECTION INTERFACE
st.markdown("### 🛠️ Configure Your Knowledge Build")
row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    selected_profile = st.selectbox("1. User Profile (The Who):", list(KNOWLEDGE_BASE["profiles"].keys()))
with row1_col2:
    selected_paradigm = st.selectbox("2. Paradigm (The View):", list(KNOWLEDGE_BASE["paradigms"].keys()))
with row1_col3:
    selected_science = st.selectbox("3. Science (The Block):", list(KNOWLEDGE_BASE["subject_details"].keys()))

row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1:
    selected_method = st.selectbox("4. Methodology (The Way):", KNOWLEDGE_BASE["subject_details"][selected_science]["methods"])
with row2_col2:
    selected_tool = st.selectbox("5. Specific Tool (The Instrument):", KNOWLEDGE_BASE["subject_details"][selected_science]["tools"])
with row2_col3:
    selected_model = st.selectbox("6. Knowledge Model (The Structure):", list(KNOWLEDGE_BASE["knowledge_models"].keys()))

user_query = st.text_area("❓ Synthesis Question:", 
                         placeholder="e.g. How do we explain consciousness through these layers?")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Run Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Please provide a Groq API Key.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_info = KNOWLEDGE_BASE["profiles"][selected_profile]
            paradigm_info = KNOWLEDGE_BASE["paradigms"][selected_paradigm]
            model_info = KNOWLEDGE_BASE["knowledge_models"][selected_model]
            
            prompt = f"""
            You are the SIS Synthesizer. Synthesize a response based on these 6 Lego dimensions:
            
            1. USER PROFILE: {selected_profile} (Driver: {p_info['drivers']})
            2. PARADIGM: {selected_paradigm} ({paradigm_info})
            3. SCIENCE FIELD: {selected_science}
            4. METHODOLOGY: {selected_method}
            5. TOOL: {selected_tool}
            6. KNOWLEDGE MODEL STRUCTURE: {selected_model} ({model_info})

            INSTRUCTIONS:
            - Foundation: Start with the {selected_paradigm} view.
            - Building Blocks: Use {selected_science} and {selected_tool} as your primary materials.
            - Architecture: Organize the logic using the {selected_model} structure (e.g., focus on causes/effects or sequences).
            - Goal: Satisfy the {selected_profile}'s core driver.
            
            Tone: Professional, academic, yet structured like a 'Lego build' explanation.
            Language: English.
            """
            
            with st.spinner('Assembling knowledge layers...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6
                )
                
                st.subheader("📊 Synthesis Result")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Global Epistemic Architecture | 2025 Edition | Multi-Dimensional Framework")
