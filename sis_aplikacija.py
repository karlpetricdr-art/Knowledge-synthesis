import streamlit as st
import json
from openai import OpenAI

# =========================================================
# 1. EXPANDED LEGO ONTOLOGY (All Major Sciences)
# =========================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {
            "subjects": ["Astronomy", "Earth Sciences", "History", "Anthropology", "Biology", "Geography"],
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
            "subjects": ["Sociology", "Political Science", "Statistics", "Ecology", "Linguistics", "Archaeology"],
            "drivers": "pattern recognition / systematic analysis",
            "description": "Detached analytical minds watching how systems and societies evolve."
        }
    },
    "subject_details": {
        "Physics": {"facets": ["quantum mechanics", "thermodynamics", "relativity", "electromagnetism", "kinetics"], "program_type": "Natural Sciences / Fundamental"},
        "Chemistry": {"facets": ["organic synthesis", "molecular bonding", "thermodynamics", "electrochemistry", "biochemistry"], "program_type": "Natural Sciences / Experimental"},
        "Biology": {"facets": ["genetics", "evolution", "cell biology", "microbiology", "physiology"], "program_type": "Natural Sciences / Life Sciences"},
        "Astronomy": {"facets": ["cosmology", "astrophysics", "planetary science", "black holes", "stellar evolution"], "program_type": "Natural Sciences / Space Exploration"},
        "Earth Sciences": {"facets": ["geology", "meteorology", "oceanography", "climatology", "paleontology"], "program_type": "Natural Sciences / Environmental"},
        "Psychology": {"facets": ["behavioral patterns", "cognition", "neuroscience", "developmental stages", "psychopathology"], "program_type": "Social Sciences / Mental Health"},
        "Sociology": {"facets": ["social stratification", "urbanization", "cultural norms", "demographics", "group dynamics"], "program_type": "Social Sciences / Societal Analysis"},
        "Economics": {"facets": ["macroeconomics", "microeconomics", "game theory", "econometrics", "market cycles"], "program_type": "Social Sciences / Financial Systems"},
        "Political Science": {"facets": ["geopolitics", "governance", "international relations", "public policy", "political theory"], "program_type": "Social Sciences / Governance"},
        "History": {"facets": ["historiography", "archaeology", "chronology", "cultural heritage", "genealogy"], "program_type": "Social Sciences / Humanities"},
        "Linguistics": {"facets": ["syntax", "semantics", "phonetics", "etymology", "sociolinguistics"], "program_type": "Social Sciences / Communications"},
        "Mathematics": {"facets": ["calculus", "linear algebra", "topology", "number theory", "discrete mathematics"], "program_type": "Formal Sciences / Abstract"},
        "Logic": {"facets": ["syllogisms", "symbolic logic", "boolean algebra", "deductive reasoning", "paradoxes"], "program_type": "Formal Sciences / Philosophy"},
        "Computer Science": {"facets": ["algorithms", "artificial intelligence", "cybersecurity", "software engineering", "data structures"], "program_type": "Formal Sciences / Technology"},
        "Statistics": {"facets": ["probability theory", "regression analysis", "variance", "data mining", "inference"], "program_type": "Formal Sciences / Data Analysis"},
        "Medicine": {"facets": ["anatomy", "pharmacology", "pathology", "immunology", "surgery"], "program_type": "Applied Sciences / Healthcare"},
        "Engineering": {"facets": ["robotics", "civil engineering", "mechanical systems", "nanotechnology", "aerospace"], "program_type": "Applied Sciences / Technical"},
        "Philosophy": {"facets": ["metaphysics", "ethics", "epistemology", "existentialism", "ontology"], "program_type": "Humanities / Theory"}
    }
}

# Categorization for the Sidebar Explorer
SCIENCE_CATEGORIES = {
    "Natural Sciences": ["Physics", "Chemistry", "Biology", "Astronomy", "Earth Sciences"],
    "Social Sciences": ["Psychology", "Sociology", "Economics", "Political Science", "History", "Linguistics"],
    "Formal Sciences": ["Mathematics", "Logic", "Computer Science", "Statistics"],
    "Applied Sciences": ["Medicine", "Engineering", "Philosophy"]
}

# =========================================================
# 2. INTERFACE (Streamlit)
# =========================================================
st.set_page_config(page_title="SIS Science Synthesizer", page_icon="🧱", layout="wide")

st.title("🧱 SIS - Universal Knowledge Synthesizer")
st.markdown("Advanced synthesis engine based on the **Lego Taxonomy of Sciences**.")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Groq API Key:", type="password")
    
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    
    # --- MODERN KNOWLEDGE EXPLORER ---
    st.subheader("📚 Knowledge Explorer")
    show_db = st.toggle("Enable Explorer View", help="Click to browse the ontology blocks.")
    
    if show_db:
        with st.expander("👤 User Profiles", expanded=True):
            for name, info in KNOWLEDGE_BASE["profiles"].items():
                st.markdown(f"**{name}**")
                st.caption(info["description"])
                st.write(f"*Drivers:* {info['drivers']}")
                st.divider()

        with st.expander("🔬 Scientific Fields"):
            for cat, subjects in SCIENCE_CATEGORIES.items():
                st.markdown(f"**{cat}**")
                # Creating small buttons/popovers for each subject
                for sub in subjects:
                    if sub in KNOWLEDGE_BASE["subject_details"]:
                        details = KNOWLEDGE_BASE["subject_details"][sub]
                        with st.popover(f"Explore {sub}", use_container_width=True):
                            st.markdown(f"### {sub}")
                            st.write(f"**Category:** {details['program_type']}")
                            st.write("**Key Facets (Lego Bricks):**")
                            for facet in details['facets']:
                                st.markdown(f"- {facet}")
                st.divider()
    else:
        st.info("SIS Model: Connects User Profiles with Science using Lego logic. Enable the Explorer to see the data structure.")

# Main Selection Interface
c1, c2 = st.columns(2)
with c1:
    profile_names = list(KNOWLEDGE_BASE["profiles"].keys())
    selected_profile = st.selectbox("👤 Select User Profile:", profile_names)
    st.info(f"**Profile focus:** {KNOWLEDGE_BASE['profiles'][selected_profile]['description']}")

with c2:
    all_subjects = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    # Default to first subject of selected profile if possible
    profile_subjects = KNOWLEDGE_BASE["profiles"][selected_profile]["subjects"]
    default_index = all_subjects.index(profile_subjects[0]) if profile_subjects[0] in all_subjects else 0
    
    selected_subject = st.selectbox("🔬 Select Scientific Field:", all_subjects, index=default_index)

user_question = st.text_area("❓ Synthesis Question:", 
                              placeholder=f"e.g., How does {selected_subject} impact the worldview of a {selected_profile}?")

# =========================================================
# 3. SYNTHESIS LOGIC (Groq AI)
# =========================================================
if st.button("🚀 Run Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing API Key! Please provide a Groq API key in the sidebar.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            p_data = KNOWLEDGE_BASE["profiles"][selected_profile]
            s_data = KNOWLEDGE_BASE["subject_details"][selected_subject]
            
            prompt = f"""
            SYSTEM ROLE: You are the SIS (Systemic Interest Synthesizer). 
            CONTEXT:
            - User Profile: {selected_profile} (Core Driver: {p_data['drivers']})
            - Science Field: {selected_subject}
            - Program Category: {s_data['program_type']}
            - Key Facets: {", ".join(s_data['facets'])}

            TASK:
            Synthesize the scientific field with the user's profile. 
            Use 'Lego Logic' - explain how the 'bricks' of {selected_subject} (the facets) 
            build into the 'structure' of the {selected_profile}'s mind.
            
            LANGUAGE: English.
            """
            
            with st.spinner('Synthesizing knowledge blocks...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_question}
                    ],
                    temperature=0.6
                )
                
                st.subheader("📊 Synthesis Result")
                st.markdown(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Global Model | 2025 Edition | Knowledge Architecture")
