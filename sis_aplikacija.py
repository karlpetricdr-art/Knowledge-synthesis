import streamlit as st
import json
from openai import OpenAI

# =========================================================
# 1. EXPANDED LEGO ONTOLOGY (Sciences + Methodologies)
# =========================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {
            "subjects": ["Astronomy", "Earth Sciences", "Anthropology", "Biology", "Geography", "Archaeology"],
            "drivers": "exploration / discovery of the unknown",
            "description": "Explorers of physical and temporal boundaries."
        },
        "Applicators": {
            "subjects": ["Medicine", "Engineering", "Computer Science", "Economics", "Chemistry", "Psychology"],
            "drivers": "practical utility / problem solving",
            "description": "Focus on applying knowledge to create tangible solutions."
        },
        "Know-it-alls": {
            "subjects": ["Physics", "Mathematics", "Philosophy", "Logic", "History", "Chemistry", "Biology", "Sociology", "Economics"],
            "drivers": "universal synthesis / absolute knowledge",
            "description": "Seek to master all disciplines and find the 'Theory of Everything'."
        },
        "Observers": {
            "subjects": ["Sociology", "Political Science", "Statistics", "Ecology", "Linguistics", "Psychology"],
            "drivers": "pattern recognition / systematic analysis",
            "description": "Detached analytical minds watching how systems and societies evolve."
        }
    },
    "subject_details": {
        # NATURAL SCIENCES
        "Physics": {
            "facets": ["quantum mechanics", "relativity", "electromagnetism", "thermodynamics"],
            "methods": ["Experimental Method", "Mathematical Modeling", "Computational Simulation", "Spectroscopy"],
            "type": "Natural Sciences"
        },
        "Chemistry": {
            "facets": ["molecular bonding", "organic synthesis", "electrochemistry", "biochemistry"],
            "methods": ["Titration", "Chromatography", "X-ray Crystallography", "Chemical Synthesis"],
            "type": "Natural Sciences"
        },
        "Biology": {
            "facets": ["genetics", "evolution", "cell biology", "microbiology"],
            "methods": ["CRISPR Gene Editing", "Microscopy", "Field Observation", "DNA Sequencing"],
            "type": "Natural Sciences"
        },
        "Astronomy": {
            "facets": ["cosmology", "astrophysics", "black holes", "stellar evolution"],
            "methods": ["Photometry", "Radio Astronomy", "Spectroscopic Analysis", "Orbital Mechanics"],
            "type": "Natural Sciences"
        },
        "Earth Sciences": {
            "facets": ["geology", "meteorology", "oceanography", "climatology"],
            "methods": ["Seismic Mapping", "Carbon Dating", "Remote Sensing", "Climate Modeling"],
            "type": "Natural Sciences"
        },
        # SOCIAL SCIENCES
        "Psychology": {
            "facets": ["behavioral patterns", "cognition", "neuroscience", "developmental stages"],
            "methods": ["Double-Blind Trials", "Case Studies", "Psychometrics", "Neuroimaging (fMRI)"],
            "type": "Social Sciences"
        },
        "Sociology": {
            "facets": ["social stratification", "cultural norms", "group dynamics", "urbanization"],
            "methods": ["Ethnography", "Statistical Surveys", "Content Analysis", "Longitudinal Studies"],
            "type": "Social Sciences"
        },
        "Economics": {
            "facets": ["macroeconomics", "microeconomics", "game theory", "market cycles"],
            "methods": ["Econometrics", "Cost-Benefit Analysis", "Game Theoretic Modeling", "Regression Analysis"],
            "type": "Social Sciences"
        },
        "Political Science": {
            "facets": ["geopolitics", "governance", "public policy", "political theory"],
            "methods": ["Comparative Analysis", "Policy Evaluation", "Discourse Analysis", "Poll Analysis"],
            "type": "Social Sciences"
        },
        "History": {
            "facets": ["historiography", "chronology", "cultural heritage", "genealogy"],
            "methods": ["Archival Research", "Paleography", "Source Criticism", "Oral History"],
            "type": "Social Sciences"
        },
        "Linguistics": {
            "facets": ["syntax", "semantics", "phonetics", "etymology"],
            "methods": ["Corpus Analysis", "Phonetic Transcription", "Comparative Linguistics", "Field Linguistics"],
            "type": "Social Sciences"
        },
        # FORMAL SCIENCES
        "Mathematics": {
            "facets": ["calculus", "linear algebra", "topology", "number theory"],
            "methods": ["Axiomatic Method", "Mathematical Proof", "Statistical Inference", "Algorithm Design"],
            "type": "Formal Sciences"
        },
        "Logic": {
            "facets": ["syllogisms", "symbolic logic", "boolean algebra", "paradoxes"],
            "methods": ["Deductive Reasoning", "Formal Verification", "Truth Tables", "Predicate Logic"],
            "type": "Formal Sciences"
        },
        "Computer Science": {
            "facets": ["algorithms", "artificial intelligence", "cybersecurity", "data structures"],
            "methods": ["Agile Development", "Big Data Analytics", "Machine Learning Training", "Heuristic Search"],
            "type": "Formal Sciences"
        },
        # APPLIED SCIENCES
        "Medicine": {
            "facets": ["anatomy", "pharmacology", "pathology", "immunology"],
            "methods": ["Clinical Trials", "Epidemiological Studies", "Diagnostic Imaging", "Biopsies"],
            "type": "Applied Sciences"
        },
        "Engineering": {
            "facets": ["robotics", "mechanical systems", "nanotechnology", "aerospace"],
            "methods": ["Prototyping", "Finite Element Analysis", "CAD Design", "Systems Engineering"],
            "type": "Applied Sciences"
        },
        "Philosophy": {
            "facets": ["metaphysics", "ethics", "epistemology", "ontology"],
            "methods": ["Socratic Method", "Phenomenology", "Conceptual Analysis", "Thought Experiments"],
            "type": "Applied Sciences / Humanities"
        }
    }
}

# Categorization for Explorer
SCIENCE_CATEGORIES = {
    "Natural Sciences": ["Physics", "Chemistry", "Biology", "Astronomy", "Earth Sciences"],
    "Social Sciences": ["Psychology", "Sociology", "Economics", "Political Science", "History", "Linguistics"],
    "Formal Sciences": ["Mathematics", "Logic", "Computer Science"],
    "Applied Sciences": ["Medicine", "Engineering", "Philosophy"]
}

# =========================================================
# 2. INTERFACE (Streamlit)
# =========================================================
st.set_page_config(page_title="SIS Universal Synthesizer", page_icon="🧱", layout="wide")

st.title("🧱 SIS - Universal Knowledge & Methodology Synthesizer")
st.markdown("Advanced engine synthesizing **Profiles**, **Sciences**, and **Research Methodologies**.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Groq API Key:", type="password")
    
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    
    # --- MODERN KNOWLEDGE EXPLORER ---
    st.subheader("📚 Knowledge Explorer")
    show_db = st.toggle("Enable Explorer View", help="Browse the Lego-like ontology of sciences and methods.")
    
    if show_db:
        with st.expander("👤 User Profiles", expanded=True):
            for name, info in KNOWLEDGE_BASE["profiles"].items():
                st.markdown(f"**{name}**")
                st.caption(info["description"])
                st.write(f"*Drivers:* {info['drivers']}")
                st.divider()

        with st.expander("🔬 Scientific Fields & Methods"):
            for cat, subjects in SCIENCE_CATEGORIES.items():
                st.markdown(f"**{cat}**")
                for sub in subjects:
                    if sub in KNOWLEDGE_BASE["subject_details"]:
                        details = KNOWLEDGE_BASE["subject_details"][sub]
                        with st.popover(f"Explore {sub}", use_container_width=True):
                            st.markdown(f"### {sub}")
                            st.write(f"**Facets:** {', '.join(details['facets'])}")
                            st.write("**Methodologies (Techniques):**")
                            for m in details['methods']:
                                st.markdown(f"- {m}")
                st.divider()
    else:
        st.info("The SIS Model connects profiles with scientific methodologies using Lego logic. Enable the Explorer to browse methods.")

# Main Selection Interface
c1, c2, c3 = st.columns(3)
with c1:
    profile_names = list(KNOWLEDGE_BASE["profiles"].keys())
    selected_profile = st.selectbox("👤 User Profile:", profile_names)
    st.info(f"**Focus:** {KNOWLEDGE_BASE['profiles'][selected_profile]['description']}")

with c2:
    all_subjects = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    profile_subjects = KNOWLEDGE_BASE["profiles"][selected_profile]["subjects"]
    default_sub_index = all_subjects.index(profile_subjects[0]) if profile_subjects[0] in all_subjects else 0
    selected_subject = st.selectbox("🔬 Scientific Field:", all_subjects, index=default_sub_index)

with c3:
    # Filter methodologies based on the selected science
    available_methods = KNOWLEDGE_BASE["subject_details"][selected_subject]["methods"]
    selected_method = st.selectbox("🛠️ Research Methodology:", available_methods)

user_question = st.text_area("❓ Synthesis Question:", 
                              placeholder=f"How can I use {selected_method} in {selected_subject} from the perspective of a {selected_profile}?")

# =========================================================
# 3. SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Run Multidimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing API Key! Please provide a Groq API key in the sidebar.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_data = KNOWLEDGE_BASE["profiles"][selected_profile]
            s_data = KNOWLEDGE_BASE["subject_details"][selected_subject]
            
            prompt = f"""
            SYSTEM ROLE: You are the SIS (Systemic Interest Synthesizer). 
            You explain complex scientific relationships using 'Lego Logic'.
            
            CONTEXT:
            - User Profile: {selected_profile} (Driver: {p_data['drivers']})
            - Science Field: {selected_subject} (Facets: {', '.join(s_data['facets'])})
            - Selected Methodology: {selected_method} (This is the tool/technique for the build)

            TASK:
            Synthesize the Science Field and the Methodology for this User Profile. 
            - Explain the Science Field as the 'Lego Bricks'.
            - Explain the Methodology as the 'Building Technique' or 'Instructions'.
            - Show how this specific 'build' helps the user satisfy their 'Core Driver'.
            
            LANGUAGE: English.
            """
            
            with st.spinner('Building knowledge structures...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_question}
                    ],
                    temperature=0.6
                )
                
                st.subheader("📊 Multidimensional Synthesis Result")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Global Model | 2025 Edition | Multi-Disciplinary Architecture")
