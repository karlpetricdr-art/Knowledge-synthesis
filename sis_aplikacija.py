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
        "Empiricism": "Knowledge based on sensory experience, experimental evidence, and data-driven induction.",
        "Rationalism": "Knowledge based on deductive logic, mathematical certainty, and innate intellectual principles.",
        "Constructivism": "Knowledge as a social and cognitive construction based on experience and context.",
        "Positivism": "Strict adherence to observable, measurable, and scientifically verifiable facts.",
        "Pragmatism": "Knowledge validated by its practical consequences and success in application."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing the chain of causes, effects, and the 'why' behind phenomena.",
        "Principles & Relations": "Focusing on constant laws, fundamental correlations, and relational structures.",
        "Episodes & Sequences": "Organizing knowledge as a chronological flow, event sequences, and narrative processes.",
        "Facts & Characteristics": "Focusing on properties of living/inanimate objects and raw observational data.",
        "Generalizations": "Moving from specific data points to broad, universal conceptual frameworks.",
        "Glossary & Concepts": "Defining precise terminologies, subject labels, and situational conceptual maps."
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
st.set_page_config(page_title="SIS Synthesizer", page_icon="🧱", layout="wide")

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Precision synthesis engine for **Personalized Knowledge Architecture**.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Groq API Key:", type="password")
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    st.subheader("📚 Knowledge Explorer")
    show_db = st.toggle("Enable Explorer Mode", help="Browse the internal ontology.")
    
    if show_db:
        with st.expander("👤 User Profiles"):
            for p, d in KNOWLEDGE_BASE["profiles"].items():
                st.write(f"**{p}**: {d['description']}")
        with st.expander("🌍 Paradigms & Models"):
            st.write("--- Paradigms ---")
            for p, d in KNOWLEDGE_BASE["paradigms"].items():
                st.write(f"*{p}*: {d}")
            st.write("--- Structures (from Image) ---")
            for m, d in KNOWLEDGE_BASE["knowledge_models"].items():
                st.write(f"*{m}*: {d}")

# MAIN SELECTION INTERFACE
st.markdown("### 🛠️ Define Your Cognitive Context")
col1, col2, col3 = st.columns(3)

with col1:
    # Profiles kept as Adventurers, Applicators, Know-it-alls, Observers
    selected_profile = st.selectbox("1. User Profile:", list(KNOWLEDGE_BASE["profiles"].keys()))
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"])

with col2:
    selected_paradigm = st.selectbox("2. Scientific Paradigm:", list(KNOWLEDGE_BASE["paradigms"].keys()))
    goal_context = st.selectbox("Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational / Teaching"])

with col3:
    selected_science = st.selectbox("3. Science Field:", list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_model = st.selectbox("4. Structural Model:", list(KNOWLEDGE_BASE["knowledge_models"].keys()))

st.divider()

col4, col5 = st.columns(2)
with col4:
    selected_method = st.selectbox("5. Methodology:", KNOWLEDGE_BASE["subject_details"][selected_science]["methods"])
with col5:
    selected_tool = st.selectbox("6. Specific Tool:", KNOWLEDGE_BASE["subject_details"][selected_science]["tools"])

user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="e.g. How do we explain the evolution of social structures using these dimensions?")

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
            You are the SIS Universal Knowledge Synthesizer. You construct knowledge using 'Lego Logic'.
            
            USER ATTRIBUTES:
            - Profile: {selected_profile} ({p_data['description']})
            - Expertise Level: {expertise} (Adjust depth, complexity, and vocabulary for this level)
            - Goal/Context: {goal_context} (Focus synthesis results on this specific intent)
            
            EPISTEMIC DIMENSIONS:
            - Paradigm: {selected_paradigm} ({KNOWLEDGE_BASE['paradigms'][selected_paradigm]})
            - Science: {selected_science}
            - Methodology: {selected_method}
            - Tool: {selected_tool}
            - Structural Model: {selected_model} ({KNOWLEDGE_BASE['knowledge_models'][selected_model]})

            CONSTRUCTION RULES:
            1. Use the Paradigm as the foundational logic for the entire answer.
            2. Use the Science and Tool as the physical 'Lego Bricks' to build the argument.
            3. Apply the Structural Model as the architectural 'Building Plan' (e.g., focus on Causal chains or Episodes).
            4. Tailor the language strictly to a {expertise} audience. 
            5. Ensure the final synthesis serves the objective of {goal_context}.

            Format the response with professional markdown headings. Output language: English.
            """
            
            with st.spinner(f'Synthesizing {expertise} level blocks for {selected_profile}...'):
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
            st.error(f"Synthesis error: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | Powered by Groq AI | 2026 Framework")
