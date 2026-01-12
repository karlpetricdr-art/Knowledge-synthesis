import streamlit as st
import json
import base64
import requests
import urllib.parse
import re
import time
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

def get_svg_base64(svg_str):
    """Pretvori SVG niz v base64 format za prikaz slike."""
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

# --- CYTOSCAPE RENDERER Z DVOSMERNO NAVIGACIJO ---
def render_cytoscape_network(elements, container_id="cy", clickable=False):
    """
    Izriše interaktivno omrežje Cytoscape.js. 
    Če je clickable=True, omogoči pomik na tekst ob kliku na vozlišče.
    """
    click_handler_js = ""
    if clickable:
        click_handler_js = """
        cy.on('tap', 'node', function(evt){
            var node = evt.target;
            var elementId = node.id();
            // Najde element v glavnem Streamlit oknu preko starševskega DOM-a
            var targetElement = window.parent.document.getElementById(elementId);
            if (targetElement) {
                targetElement.scrollIntoView({behavior: "smooth", block: "center"});
                // Vizualni poudarek tarče
                targetElement.style.backgroundColor = "#ffffcc";
                setTimeout(function(){ targetElement.style.backgroundColor = "transparent"; }, 2500);
            }
        });
        """

    cyto_html = f"""
    <div id="{container_id}" style="width: 100%; height: 500px; background: #ffffff; border-radius: 15px; border: 1px solid #eee; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);"></div>
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
                            'width': 65,
                            'height': 65,
                            'font-size': '11px',
                            'font-weight': 'bold',
                            'text-outline-width': 2,
                            'text-outline-color': '#fff',
                            'cursor': 'pointer',
                            'box-shadow': '0px 4px 6px rgba(0,0,0,0.2)'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 3,
                            'line-color': '#ddd',
                            'label': 'data(label)',
                            'font-size': '8px',
                            'target-arrow-color': '#ddd',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'text-rotation': 'autorotate'
                        }}
                    }}
                ],
                layout: {{ name: 'cose', padding: 40, animate: true, nodeRepulsion: 10000 }}
            }});
            {click_handler_js}
        }});
    </script>
    """
    components.html(cyto_html, height=520)

# --- PRIDOBIVANJE BIBLIOGRAFIJ (ORCID / SCHOLAR) ---
def fetch_author_bibliographies(author_input):
    """Zajame bibliografske podatke o delih več avtorjev preko ORCID in Scholar Proxy."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        # Poskus iskanja ORCID ID-ja preko imena
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
                else: comprehensive_biblio += "No public works found.\n"
            except: pass
        else:
            # Poskus iskanja preko Semantic Scholar
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
        "Physics": {
            "cat": "Natural Sciences",
            "methods": ["Mathematical Modeling", "Experimental Method", "Simulation"],
            "tools": ["Particle Accelerator", "Spectrometer", "Interferometer"],
            "facets": ["Quantum Mechanics", "Relativity", "Thermodynamics"]
        },
        "Chemistry": {
            "cat": "Natural Sciences",
            "methods": ["Chemical Synthesis", "Spectroscopy", "Chromatography"],
            "tools": ["NMR Spectrometer", "Mass Spectrometer", "Electron Microscope"],
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
            "tools": ["IDE (VS Code)", "LLM + LangChain + LLMGraphTransformer", "Markmap", "Git"],
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
            "methods": ["Taxonomic Classification", "Archival Appraisal", "Bibliometrics"],
            "tools": ["OPAC Systems", "Metadata Schemas", "Digital Repositories"],
            "facets": ["Information Retrieval", "Knowledge Organization"]
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
# 2. STREAMLIT INTERFACE KONSTRUKCIJA
# =========================================================

# --- SESSION STATE INICIALIZACIJA ---
if 'expertise_val' not in st.session_state: 
    st.session_state.expertise_val = "Intermediate"
if 'show_user_guide' not in st.session_state:
    st.session_state.show_user_guide = False

# --- STRANSKA VRSTICA (SIDEBAR) ---
with st.sidebar:
    st.markdown(
        f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', 
        unsafe_allow_html=True
    )
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    # --- VODIČ ZA UPORABO (Interaktiven gumb) ---
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()

    if st.session_state.show_user_guide:
        st.info("""
        1. **API Key**: Enter your Groq API key for high-speed synthesis.
        2. **User Profile**: Select a cognitive style that fits your thinking process.
        3. **Authors**: Provide names (e.g., Karl Petrič) for real-time ORCID data.
        4. **Select Dimensions**: Choose from 12 scientific fields and multiple structural models.
        5. **Synthesis Inquiry**: Provide a complex interdisciplinary question.
        6. **Interactive Navigation**: Click any node in the Semantic Graph to scroll to its definition.
        7. **Backlinks**: Click [↑] in the text to return to the graph visualization.
        """)
        if st.button("Close Guide ✖️"):
            st.session_state.show_user_guide = False
            st.rerun()
    
    # API ključ iz skrivnosti (če obstaja)
    if not api_key and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    st.subheader("📚 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.write(f"**{p}**: {d['description']}")
    with st.expander("🧠 Mental Approaches"):
        for a in KNOWLEDGE_BASE["mental_approaches"]:
            st.write(f"• {a}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items():
            st.write(f"**{p}**: {d}")
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            st.write(f"• **{s}**")
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items():
            st.write(f"**{m}**: {d}")
    
    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    # --- SOCIALNI/VIRSKI GUMBI ---
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

# --- GLAVNI VMESNIK ZA KONFIGURACIJO ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis engine with **Bi-directional Semantic Linking**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# ROW 1: RESEARCH AUTHORS
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input(
        "👤 Research Authors:", 
        value="", 
        placeholder="e.g. Karl Petrič, Samo Kralj, Teodor Petrič"
    )
    st.caption("Active connectivity for real-time bibliographic synergy analysis via ORCID/Scholar API.")

# ROW 2: PROFILES, SCIENCES, EXPERTISE
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    selected_profiles = st.multiselect(
        "1. User Profiles:", 
        list(KNOWLEDGE_BASE["profiles"].keys()), 
        default=["Adventurers"]
    )
with r2_c2:
    sciences_list = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    selected_sciences = st.multiselect(
        "2. Science Fields:", 
        sciences_list, 
        default=["Computer Science", "Sociology", "Philosophy"]
    )
with r2_c3:
    expertise = st.select_slider(
        "3. Expertise Level:", 
        options=["Novice", "Intermediate", "Expert"], 
        value=st.session_state.expertise_val
    )

# ROW 3: MODELS, PARADIGMS, GOAL
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1:
    selected_models = st.multiselect(
        "4. Structural Models:", 
        list(KNOWLEDGE_BASE["knowledge_models"].keys()), 
        default=["Concepts", "Causal Connections"]
    )
with r3_c2:
    selected_paradigms = st.multiselect(
        "5. Scientific Paradigms:", 
        list(KNOWLEDGE_BASE["paradigms"].keys()), 
        default=["Rationalism", "Pragmatism"]
    )
with r3_c3:
    goal_context = st.selectbox(
        "6. Context / Goal:", 
        ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"]
    )

# ROW 4: APPROACHES, METHODS, TOOLS
r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1:
    selected_approaches = st.multiselect(
        "7. Mental Approaches:", 
        KNOWLEDGE_BASE["mental_approaches"], 
        default=["Perspective shifting", "Associativity"]
    )

# Dinamična agregacija metod in orodij glede na izbrane vede
agg_methods = []
agg_tools = []
for s in selected_sciences:
    if s in KNOWLEDGE_BASE["subject_details"]:
        agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
        agg_tools.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

with r4_c2:
    selected_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_methods))))
with r4_c3:
    selected_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tools))))

st.divider()
user_query = st.text_area(
    "❓ Your Synthesis Inquiry:", 
    placeholder="Create a synergy and synthesized knowledge for better resolving global problems like crime, distress, mass migration and poverty"
)

# =========================================================
# 3. JEDRO SINTEZE: GROQ AI + SEMANTIČNO POVEZOVANJE
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key. Please provide it in the Sidebar.")
    elif not user_query:
        st.warning("Please enter your synthesis inquiry.")
    else:
        try:
            # --- 1. PRIDOBIVANJE METAPODATKOV AVTORJEV ---
            synergy_biblio = ""
            if target_authors:
                with st.spinner(f'Fetching research metadata for {target_authors}...'):
                    synergy_biblio = fetch_author_bibliographies(target_authors)

            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # Anchor za skok nazaj na graf
            st.markdown('<div id="semantic_graph_anchor"></div>', unsafe_allow_html=True)
            
            # --- 2. KONSTRUKCIJA SISTEMSKEGA NAVODILA (LONG-FORM) ---
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. Perform an exhaustive, long-form interdisciplinary dissertation (minimum 1200 words).
            
            STRICT RESEARCH CONTEXT:
            {synergy_biblio if synergy_biblio else "No specific author data found. Use your deep internal scientific training."}

            REQUIREMENTS:
            - Create a high-fidelity synergy between the selected Science Fields: {", ".join(selected_sciences)}.
            - Use the following Scientific Paradigms: {", ".join(selected_paradigms)}.
            - Apply structural thinking from: {", ".join(selected_models)}.
            - Focus on the Context: {goal_context}.
            - Structure the analysis into multiple thematic layers with deep causal explanations.
            - Address the user inquiry concerning global issues (crime, migration, poverty) with innovative solutions.

            LLMGraphTransformer OUTPUT REQUIREMENT:
            After the markdown synthesis, add the exact delimiter: ### SEMANTIC_GRAPH_JSON
            Then provide a valid JSON object ONLY: 
            {{
              "nodes": [
                {{"id": "node_id", "label": "Concept Name", "color": "#2a9d8f"}}
              ],
              "edges": [
                {{"source": "node_id", "target": "node_id_2", "label": "relationship"}}
              ]
            }}
            Identify at least 8-12 key conceptual nodes from your synthesis.
            """
            
            with st.spinner('Synthesizing exhaustive research synergy (8–40 seconds)...'):
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
                
                # --- 3. PARSIRANJE IZHODA IN DVOSMERNO POVEZOVANJE ---
                parts = full_raw_output.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # Če imamo JSON podatke, pripravimo besedilo za povratne linke
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            # Vstavimo HTML ID-je v besedilo za vsako vozlišče (samo prva ponovitev)
                            # Zraven dodamo [↑] link, ki vrne na sidro 'semantic_graph_anchor'
                            for node in graph_data.get("nodes", []):
                                label = node["label"]
                                node_id = node["id"]
                                pattern = re.compile(re.escape(label), re.IGNORECASE)
                                replacement = f'<span id="{node_id}" style="color:#2a9d8f; font-weight:bold; border-bottom:1px dashed #2a9d8f;">{label} <a href="#semantic_graph_anchor" style="text-decoration:none; font-size:10px; color:#aaa;">[↑]</a></span>'
                                main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                # --- 4. PRIKAZ REZULTATOV ---
                st.subheader("📊 Synthesis Output")
                # unsafe_allow_html=True je ključen za delovanje ID-jev in navigacije
                st.markdown(main_markdown, unsafe_allow_html=True)

                # Vizualizacija Semantičnega Grafa
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            st.subheader("🕸️ LLMGraphTransformer: Semantic Knowledge Graph")
                            st.caption("Click Concept Nodes to scroll to their definitions in the text. Click [↑] in text to return to graph.")
                            
                            semantic_elements = []
                            for n in graph_data.get("nodes", []):
                                semantic_elements.append({
                                    "data": {"id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f")}
                                })
                            for e in graph_data.get("edges", []):
                                semantic_elements.append({
                                    "data": {"source": e["source"], "target": e["target"], "label": e.get("label", "correlates")}
                                })
                            
                            render_cytoscape_network(semantic_elements, "semantic_viz_container", clickable=True)
                    except:
                        st.warning("Could not parse the semantic graph JSON data.")

                # Vizualizacija vhodne konfiguracije
                st.subheader("📍 Structural Configuration Map")
                input_nodes = [{"data": {"id": "q", "label": "INQUIRY", "color": "#e63946"}}]
                input_edges = []
                for s in selected_sciences:
                    input_nodes.append({"data": {"id": s, "label": s, "color": "#f4a261"}})
                    input_edges.append({"data": {"source": "q", "target": s, "label": "discipline"}})
                for p in selected_profiles:
                    input_nodes.append({"data": {"id": p, "label": p, "color": "#457b9d"}})
                    input_edges.append({"data": {"source": "q", "target": p, "label": "profile"}})

                render_cytoscape_network(input_nodes + input_edges, "input_map_container")
                
                # Prikaz metapodatkov iz baz
                if synergy_biblio:
                    with st.expander("📚 View Metadata Fetched from Research Databases"):
                        st.text(synergy_biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v7.1 Fully Interactive 12D Semantic Linking Edition | 2026")
