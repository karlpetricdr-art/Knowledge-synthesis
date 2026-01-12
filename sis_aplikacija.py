import streamlit as st
import json
import base64
import requests
import urllib.parse
import re
import time
from datetime import datetime
from openai import OpenAI
import streamlit.components.v1 as components

# =========================================================
# 0. KONFIGURACIJA IN POMOŽNE FUNKCIJE
# =========================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Po meri narejen CSS za vizualno poudarjanje semantičnih pojmov
st.markdown("""
<style>
    .semantic-node-highlight {
        color: #2a9d8f;
        font-weight: bold;
        border-bottom: 2px solid #2a9d8f;
        padding: 0 2px;
        background-color: #f0fdfa;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Pretvori SVG niz v base64 format za varno vstavljanje v HTML slike."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF (Embedded SVG) ---
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

# --- CYTOSCAPE RENDERER Z NAVIGACIJO (Click-to-Scroll) ---
def render_cytoscape_network(elements, container_id="cy", clickable=True):
    """
    Izriše interaktivno omrežje Cytoscape.js. 
    Ob kliku na vozlišče se stran samodejno pomakne na ustrezno definicijo v besedilu.
    """
    click_handler_js = """
    cy.on('tap', 'node', function(evt){
        var node = evt.target;
        var elementId = node.id();
        // Dostop do starševskega DOM-a Streamlita za navigacijo
        var targetElement = window.parent.document.getElementById(elementId);
        if (targetElement) {
            targetElement.scrollIntoView({behavior: "smooth", block: "center"});
            // Vizualni poudarek tarče ob skoku
            targetElement.style.backgroundColor = "#ffffcc";
            setTimeout(function(){ targetElement.style.backgroundColor = "transparent"; }, 2500);
        }
    });
    """

    cyto_html = f"""
    <div id="{container_id}" style="width: 100%; height: 550px; background: #ffffff; border-radius: 15px; border: 1px solid #eee; box-shadow: 2px 2px 12px rgba(0,0,0,0.05);"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'color': '#333',
                            'background-color': 'data(color)',
                            'width': 70,
                            'height': 70,
                            'font-size': '11px',
                            'font-weight': 'bold',
                            'text-outline-width': 2,
                            'text-outline-color': '#fff',
                            'cursor': 'pointer',
                            'box-shadow': '0px 4px 6px rgba(0,0,0,0.1)'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 3,
                            'line-color': '#ddd',
                            'label': 'data(label)',
                            'font-size': '9px',
                            'target-arrow-color': '#ddd',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'text-rotation': 'autorotate'
                        }}
                    }}
                ],
                layout: {{ name: 'cose', padding: 50, animate: true, nodeRepulsion: 15000 }}
            }});
            {click_handler_js}
        }});
    </script>
    """
    components.html(cyto_html, height=580)

def fetch_author_bibliographies(author_input):
    """Zajame bibliografske podatke preko ORCID API za vključitev v raziskovalni kontekst."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers=headers, timeout=5).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass

        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID BIBLIOGRAPHY: {auth.upper()} ({orcid_id}) ---\n"
                if works:
                    for work in works[:5]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                        comprehensive_biblio += f"- {title}\n"
                else: comprehensive_biblio += "No public works found in ORCID record.\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=3&fields=title,year"
                ss_res = requests.get(ss_url, timeout=5).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR BIBLIOGRAPHY: {auth.upper()} ---\n"
                    for p in papers:
                        comprehensive_biblio += f"- {p['title']} ({p.get('year','n.d.')})\n"
            except: pass
    return comprehensive_biblio

# =========================================================
# 1. THE ADVANCED MULTIDIMENSIONAL ONTOLOGY (FULL 12 FIELDS)
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
        "Adventurers": {"drivers": "discovery", "description": "Explorers seeking hidden patterns."},
        "Applicators": {"drivers": "utility", "description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"drivers": "synthesis", "description": "Systemic thinkers seeking absolute clarity."},
        "Observers": {"drivers": "evolution", "description": "Detached analysts who monitor systems."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience and induction.",
        "Rationalism": "Knowledge based on deductive logic and innate principles.",
        "Constructivism": "Knowledge as a social construction.",
        "Positivism": "Strict adherence to scientific facts.",
        "Pragmatism": "Knowledge validated by practical success."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes, effects, and the 'why'.",
        "Principles & Relations": "Constant laws and fundamental correlations.",
        "Episodes & Sequences": "Organizing knowledge as a chronological flow.",
        "Facts & Characteristics": "Raw data and properties of objects.",
        "Generalizations": "Broad, universal conceptual frameworks.",
        "Glossary": "Precise definitions of terminology.",
        "Concepts": "Abstract mental constructs and situational maps."
    },
    "subject_details": {
        "Physics": {"cat": "Natural Sciences", "methods": ["Mathematical Modeling", "Simulation"], "tools": ["Particle Accelerator", "Spectrometer"], "facets": ["Quantum Mechanics", "Relativity"]},
        "Chemistry": {"cat": "Natural Sciences", "methods": ["Chemical Synthesis", "Spectroscopy"], "tools": ["NMR Spectrometer", "Chromatography"], "facets": ["Molecular Bonding", "Organic Chemistry"]},
        "Biology": {"cat": "Natural Sciences", "methods": ["DNA Sequencing", "CRISPR Editing"], "tools": ["Gene Sequencer", "Confocal Microscope"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural Sciences", "methods": ["Neuroimaging", "Electrophysiology"], "tools": ["fMRI Scanner", "EEG"], "facets": ["Neuroplasticity", "Cognitive Mapping"]},
        "Psychology": {"cat": "Social Sciences", "methods": ["Double-Blind Trials", "Psychometrics"], "tools": ["fMRI Scanner", "EEG"], "facets": ["Behavioral Cognition", "Developmental"]},
        "Sociology": {"cat": "Social Sciences", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics Software", "Network Analysis Tools"], "facets": ["Social Stratification", "Group Dynamics"]},
        "Computer Science": {"cat": "Formal Sciences", "methods": ["Algorithm Design", "Formal Verification"], "tools": ["IDE", "LLMGraphTransformer", "GPU Clusters", "Git"], "facets": ["Artificial Intelligence", "Cybersecurity"]},
        "Medicine": {"cat": "Applied Sciences", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT Scanners", "Stethoscopes", "Bio-Markers"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied Sciences", "methods": ["Prototyping", "FEA Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotechnology"]},
        "Library Science": {"cat": "Applied Sciences", "methods": ["Taxonomic Classification", "Bibliometrics"], "tools": ["OPAC Systems", "Metadata Schemas"], "facets": ["Information Retrieval", "Knowledge Organization"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Conceptual Analysis"], "tools": ["Library Archives", "Logic Mapping Tools"], "facets": ["Ethics", "Epistemology"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK Toolkit"], "facets": ["Sociolinguistics", "Computational Linguistics"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE KONSTRUKCIJA
# =========================================================

# --- SESSION STATE INICIALIZACIJA ---
if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- STRANSKA VRSTICA (SIDEBAR) ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    # --- USER GUIDE (Interactive clickable button) ---
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()

    if st.session_state.show_user_guide:
        st.info("""
        1. **API Key**: First, enter your Groq API key to activate the synthesis engine.
        2. **User Profile**: Select the cognitive style that best suits your inquiry approach.
        3. **Authors**: Provide author names (e.g., Karl Petrič) to include real ORCID metadata.
        4. **Select Dimensions**: Choose from 12 scientific fields and multiple structural paradigms.
        5. **Inquiry**: Describe a complex, interdisciplinary problem in the large text area.
        6. **Interactive Graph**: Click nodes in the Semantic Knowledge Graph to jump to their text definitions.
        7. **Resources**: Use the links below to access GitHub, ORCID registry, or Google Scholar.
        """)
        if st.button("Close Guide ✖️"):
            st.session_state.show_user_guide = False
            st.rerun()

    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    st.subheader("📚 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🧠 Mental Approaches"):
        for a in KNOWLEDGE_BASE["mental_approaches"]: st.write(f"• {a}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items(): st.write(f"**{p}**: {d}")
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()): st.write(f"• **{s}**")
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items(): st.write(f"**{m}**: {d}")
    
    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear(); st.rerun()
    
    # --- EXTERNAL RESOURCE BUTTONS ---
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

# --- GLAVNI VMESNIK ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis engine with **LLMGraphTransformer Semantic Architecture**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# VRSTICA 1: RAZISKOVALNI AVTORJI (Z zahtevanimi primeri)
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
    st.caption("Connectivity for real-time bibliographic synergy analysis via ORCID.")

# VRSTICA 2: PROFILI, VEDE IN STROKOVNOST
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2:
    selected_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Computer Science", "Sociology", "Philosophy"])
with r2_c3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

# VRSTICA 3: MODELI, PARADIGME IN KONTEKST
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1:
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])
with r3_c2:
    selected_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Pragmatism"])
with r3_c3:
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Educational", "Policy Making"])

# VRSTICA 4: PRISTOPI, METODE IN ORODJA
r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1:
    selected_approaches = st.multiselect("7. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Associativity"])

# Agregacija metod in orodij glede na izbrane vede
agg_meth, agg_tool = [], []
for s in selected_sciences:
    agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_tool.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

with r4_c2:
    selected_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))))
with r4_c3:
    selected_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tool))))

st.divider()
# POIZVEDBA (Placeholder z zahtevanim besedilom)
user_query = st.text_area(
    "❓ Your Synthesis Inquiry:", 
    placeholder="Create a synergy and synthesized knowledge for better resolving global problems like crime, distress, mass migration and poverty",
    height=150
)

# =========================================================
# 3. JEDRO SINTEZE: GROQ AI + LLMGRAPHTRANSFORMER
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key. Please enter it in the sidebar.")
    elif not user_query:
        st.warning("Please provide an inquiry for the synthesis engine.")
    else:
        try:
            # 1. PRIDOBIVANJE BIBLIOGRAFIJ
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # 2. KONSTRUKCIJA SISTEMSKEGA NAVODILA (Dissertation level)
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. Perform an exhaustive, long-form interdisciplinary dissertation (minimum 1200 words).
            
            STRICT CONTEXT:
            - Authors metadata: {biblio if biblio else "None provided. Use internal scientific knowledge."}
            - Science Fields: {", ".join(selected_sciences)}.
            - Paradigms: {", ".join(selected_paradigms)}.
            - Models: {", ".join(selected_models)}.

            EXHAUSTIVE ANALYSIS REQUIREMENTS:
            - Analyze the core inquiry ({user_query}) through multiple thematic layers.
            - Synthesize cross-disciplinary solutions for global problems like crime, distress, migration and poverty.
            - Maintain an academic tone but prioritize innovative 'Lego Logic' synthesis.

            LLMGraphTransformer OUTPUT:
            After the markdown dissertation, add exactly: ### SEMANTIC_GRAPH_JSON
            Then provide a valid JSON object only:
            {{
              "nodes": [{{"id": "n1", "label": "Concept Name", "color": "#2a9d8f"}}],
              "edges": [{{"source": "n1", "target": "n2", "label": "causal_link"}}]
            }}
            MANDATORY: Connect concepts to EACH OTHER (semantic interconnections), not just to a central node.
            """
            
            with st.spinner('Performing high-fidelity synthesis and semantic mapping (8–40 seconds)...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.6,
                    max_tokens=4000
                )
                
                full_raw_output = response.choices[0].message.content
                parts = full_raw_output.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- PROCESIRANJE BESEDILA ZA KLIKANJE (ID Anchors) ---
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            # V besedilo vstavimo HTML ID-je za navigacijo (za vsak unikaten koncept)
                            for node in graph_data.get("nodes", []):
                                label, nid = node["label"], node["id"]
                                pattern = re.compile(re.escape(label), re.IGNORECASE)
                                replacement = f'<span id="{nid}" class="semantic-node-highlight">{label}</span>'
                                main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                # PRIKAZ REZULTATOV
                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # SEMANTIČNI GRAF (LLMGraphTransformer)
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            st.subheader("🕸️ LLMGraphTransformer: Interconnected Semantic Graph")
                            st.caption("Causal conceptual network. Click nodes to scroll to their primary definition in the text above.")
                            
                            semantic_elements = []
                            for n in graph_data.get("nodes", []):
                                semantic_elements.append({"data": {"id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f")}})
                            for e in graph_data.get("edges", []):
                                semantic_elements.append({"data": {"source": e["source"], "target": e["target"], "label": e.get("label", "interconnects")}})
                            
                            render_cytoscape_network(semantic_elements, "semantic_viz_box", clickable=True)
                    except:
                        st.warning("Could not render the semantic graph data.")

                # Razširljiv razdelek za bibliografske metapodatke
                if biblio:
                    with st.expander("📚 View Metadata Fetched from Research Databases"):
                        st.text(biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v8.1 Full 12D Interconnected Dissertation Edition | 2026")
