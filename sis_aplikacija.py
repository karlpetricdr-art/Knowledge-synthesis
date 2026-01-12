import streamlit as st
import json
import base64
import requests
import urllib.parse
import re
from openai import OpenAI
import streamlit.components.v1 as components

# =========================================================
# 0. POMOŽNE FUNKCIJE IN LOGO (Embedded SVG)
# =========================================================
def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

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

# --- CYTOSCAPE RENDERER Z JS NAVIGACIJO ---
def render_cytoscape_network(elements, container_id="cy", clickable=False):
    """Izriše interaktivno omrežje Cytoscape.js z možnostjo scroll-to-text."""
    click_js = ""
    if clickable:
        click_js = """
        cy.on('tap', 'node', function(evt){
            var node = evt.target;
            var elementId = node.id();
            // Poskus navigacije v parent oknu
            var target = window.parent.document.getElementById(elementId);
            if (target) {
                target.scrollIntoView({behavior: "smooth", block: "center"});
                target.style.backgroundColor = "#ffffcc";
                setTimeout(function(){ target.style.backgroundColor = "transparent"; }, 2000);
            }
        });
        """

    cyto_html = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <div id="{container_id}" style="width: 100%; height: 500px; background: #ffffff; border-radius: 15px; border: 1px solid #eee;"></div>
    <script>
        var cy = cytoscape({{
            container: document.getElementById('{container_id}'),
            elements: {json.dumps(elements)},
            style: [
                {{ selector: 'node', style: {{ 
                    'label': 'data(label)', 
                    'text-valign': 'center', 
                    'color': '#333', 
                    'background-color': 'data(color)',
                    'width': 55, 'height': 55,
                    'font-size': '11px',
                    'font-weight': 'bold',
                    'text-outline-width': 2,
                    'text-outline-color': '#fff',
                    'cursor': 'pointer'
                }} }},
                {{ selector: 'edge', style: {{ 
                    'width': 3, 
                    'line-color': '#ddd', 
                    'label': 'data(label)',
                    'font-size': '9px',
                    'target-arrow-color': '#ddd', 
                    'target-arrow-shape': 'triangle', 
                    'curve-style': 'bezier',
                    'text-rotation': 'autorotate'
                }} }}
            ],
            layout: {{ name: 'cose', padding: 40, animate: true }}
        }});
        {click_js}
    </script>
    """
    components.html(cyto_html, height=520)

def fetch_author_bibliographies(author_input):
    """Zajame bibliografske podatke preko ORCID in Semantic Scholar."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        if len(auth) == 19 and auth.count('-') == 3:
            orcid_id = auth
        else:
            try:
                search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
                s_res = requests.get(search_url, headers=headers, timeout=8).json()
                if s_res.get('result'):
                    orcid_id = s_res['result'][0]['orcid-identifier']['path']
            except: pass

        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=8).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID BIBLIOGRAPHY: {auth.upper()} ({orcid_id}) ---\n"
                if works:
                    for work in works[:5]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                        comprehensive_biblio += f"- {title}\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=3&fields=title,year"
                ss_res = requests.get(ss_url, timeout=8).json()
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
    "mental_approaches": ["Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)", "Condensation", "Constant", "Associativity"],
    "profiles": {
        "Adventurers": {"description": "Explorers seeking hidden patterns."},
        "Applicators": {"description": "Pragmatic minds focused on efficiency."},
        "Know-it-alls": {"description": "Systemic thinkers seeking absolute clarity."},
        "Observers": {"description": "Detached analysts who monitor systems."}
    },
    "paradigms": {"Empiricism": "Based on sensory experience.", "Rationalism": "Based on logic.", "Constructivism": "Socially constructed.", "Positivism": "Scientific facts.", "Pragmatism": "Practical success."},
    "knowledge_models": {"Causal Connections": "Why and how.", "Principles & Relations": "Fundamental laws.", "Episodes & Sequences": "Chronology.", "Facts & Characteristics": "Raw data.", "Generalizations": "Universal frameworks.", "Glossary": "Terminology.", "Concepts": "Abstract constructs."},
    "subject_details": {
        "Physics": {"methods": ["Mathematical Modeling", "Simulation"], "tools": ["Particle Accelerator", "Spectrometer"], "facets": ["Quantum Mechanics", "Relativity"]},
        "Chemistry": {"methods": ["Chemical Synthesis", "Spectroscopy"], "tools": ["NMR Spectrometer", "Electron Microscope"], "facets": ["Organic Chemistry", "Molecular Bonding"]},
        "Biology": {"methods": ["DNA Sequencing", "CRISPR Editing"], "tools": ["Gene Sequencer", "Confocal Microscope"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"methods": ["Neuroimaging", "Electrophysiology"], "tools": ["fMRI Scanner", "EEG"], "facets": ["Neuroplasticity", "Cognitive Mapping"]},
        "Psychology": {"methods": ["Double-Blind Trials", "Psychometrics"], "tools": ["Standardized Testing"], "facets": ["Behavioral Cognition", "Developmental"]},
        "Sociology": {"methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics Software"], "facets": ["Social Stratification", "Group Dynamics"]},
        "Computer Science": {"methods": ["Algorithm Design", "Formal Verification"], "tools": ["LLM + LangChain + LLMGraphTransformer", "Plotly Treemap", "streamlit-markmap"], "facets": ["Artificial Intelligence", "Knowledge Graphs"]},
        "Medicine": {"methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT Scanners", "Bio-Markers"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"methods": ["Prototyping", "Finite Element Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Structural Dynamics"]},
        "Library Science": {"methods": ["Taxonomic Classification", "Bibliometrics"], "tools": ["OPAC Systems", "Metadata Schemas"], "facets": ["Information Retrieval", "Knowledge Organization"]},
        "Philosophy": {"methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Mapping Tools"], "facets": ["Epistemology", "Ethics"]},
        "Linguistics": {"methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK"], "facets": ["Sociolinguistics", "Computational Linguistics"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine with **Interactive LLMGraphTransformer Architecture**.")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()

    if st.session_state.show_user_guide:
        st.info("""
        1. **API Key**: Enter your Groq API key for AI-driven synthesis.
        2. **User Profile**: Select your cognitive thinking style (e.g., Adventurer).
        3. **Science Fields**: Interconnect multiple academic disciplines (up to 12).
        4. **Parameter Settings**: Fine-tune expertise levels, models, and paradigms.
        5. **Research Authors**: Input names to fetch real bibliographic data via ORCID.
        6. **Submit Inquiry**: Describe the specific complex problem you want to synthesize.
        7. **Interactive Results**: Click nodes in the Semantic Graph to scroll to their definitions in the text.
        """)
        if st.button("Close Guide ✖️"):
            st.session_state.show_user_guide = False
            st.rerun()
        
    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]
    
    st.divider()
    st.subheader("🚀 Quick Templates")
    col_t1, col_t2 = st.columns(2)
    if col_t1.button("🎓 Academic", use_container_width=True):
        st.session_state.expertise_val = "Expert"
        st.rerun()
    if col_t2.button("👶 Learner", use_container_width=True):
        st.session_state.expertise_val = "Novice"
        st.rerun()

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
        st.session_state.clear()
        st.rerun()
    
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

# --- CONFIGURE INTERFACE (4 ROWS) ---
st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
    st.caption("Active connectivity for real-time bibliographic synergy analysis via ORCID.")

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2: selected_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Computer Science"])
with r2_c3: expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1: selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])
with r3_c2: selected_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with r3_c3: goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Personal Growth", "Problem Solving", "Educational"])

r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1: selected_approaches = st.multiselect("7. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=[KNOWLEDGE_BASE["mental_approaches"][0]])

agg_methods, agg_tools = [], []
for s in selected_sciences:
    agg_methods.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_tools.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

with r4_c2: selected_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_methods))))
with r4_c3: selected_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tools))))

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Provide a deep interdisciplinary inquiry...")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Groq AI + Dual Cytoscape)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key:
        st.error("Missing Groq API Key.")
    elif not selected_sciences:
        st.warning("Please select at least one Science Field.")
    else:
        try:
            synergy_biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            system_prompt = f"""
            You are the SIS Universal Knowledge Synthesizer. Build a 'Lego Logic' architecture.
            
            STRICT RESEARCH CONTEXT (Active ORCID Metadata):
            {synergy_biblio if synergy_biblio else "No specific author data found. Use internal scientific training."}

            COMPREHENSIVENESS REQUIREMENT:
            - Provide a long-form, multi-layered interdisciplinary analysis (at least 800 words).
            - Integrate selected fields: {", ".join(selected_sciences)}.
            - Use academic depth combined with innovative synthesis.

            LLMGraphTransformer TASK:
            - Extract a semantic knowledge graph from your synthesis for visualization.
            
            STRICT OUTPUT FORMAT:
            1. Detailed Markdown synthesis with clearly defined concepts.
            2. At the very end, add the delimiter: ### SEMANTIC_KNOWLEDGE_GRAPH_JSON
            3. Followed by a valid JSON block ONLY: {{"nodes": [{{"id": "node_id", "label": "Concept Name", "color": "#hex"}}], "edges": [{{"source": "node_id", "target": "node_id_2", "label": "relationship"}}]}}
            """
            
            with st.spinner('Synthesizing high-fidelity research synergy...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6,
                    max_tokens=4000
                )
                
                full_raw_output = response.choices[0].message.content
                parts = full_raw_output.split("### SEMANTIC_KNOWLEDGE_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- PROCESS MARKDOWN FOR CLICKABLE ANCHORS ---
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            for node in graph_data.get("nodes", []):
                                label, nid = node["label"], node["id"]
                                pattern = re.compile(re.escape(label), re.IGNORECASE)
                                replacement = f'<span id="{nid}" style="color:#2a9d8f; font-weight:bold; border-bottom:1px dashed #2a9d8f;">{label}</span>'
                                main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # --- VIZUALIZACIJA 1: SEMANTIČNI GRAF ---
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            st.subheader("🕸️ LLMGraphTransformer: Semantic Knowledge Graph")
                            st.caption("Click any concept node to scroll to its definition in the text above.")
                            
                            semantic_elements = []
                            for n in graph_data.get("nodes", []):
                                semantic_elements.append({"data": {"id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f")}})
                            for e in graph_data.get("edges", []):
                                semantic_elements.append({"data": {"source": e["source"], "target": e["target"], "label": e.get("label", "connects")}})
                            
                            render_cytoscape_network(semantic_elements, "semantic_viz", clickable=True)
                    except: st.warning("Graph data parsing failed.")

                # --- VIZUALIZACIJA 2: INPUT MAP ---
                st.subheader("📍 Input Synergy Map")
                input_nodes = [{"data": {"id": "q", "label": "INQUIRY", "color": "#e63946"}}]
                input_edges = []
                for s in selected_sciences:
                    input_nodes.append({"data": {"id": s, "label": s, "color": "#f4a261"}})
                    input_edges.append({"data": {"source": "q", "target": s, "label": "discipline"}})
                render_cytoscape_network(input_nodes + input_edges, "input_viz")
                
                if synergy_biblio:
                    with st.expander("📚 View Fetched Metadata"):
                        st.text(synergy_biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v5.9 Interactive Semantic Graph Edition | 2026")
