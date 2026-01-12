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
# 0. KONFIGURACIJA IN POMOŽNE FUNKCIJE (CSS & SVG)
# =========================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Po meri narejen CSS za vizualne poudarke v besedilu
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
    """Pretvori SVG v base64 za prikaz logotipa."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF ---
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

# --- TRAFFIC LOGGING SISTEM ---
if 'traffic_log' not in st.session_state:
    st.session_state.traffic_log = []

def log_api_transaction(status, duration):
    """Zabeleži Groq API klic za analitiko prometa."""
    st.session_state.traffic_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "status": status,
        "latency": f"{duration:.2f}s"
    })

# --- CYTOSCAPE VIZUALIZACIJA (Interaktivna) ---
def render_cytoscape_network(elements, container_id="cy", clickable=False):
    """Renderiranje Cytoscape.js omrežja z JS navigacijo."""
    click_js = ""
    if clickable:
        click_js = """
        cy.on('tap', 'node', function(evt){
            var node = evt.target;
            var elementId = node.id();
            var target = window.parent.document.getElementById(elementId);
            if (target) {
                target.scrollIntoView({behavior: "smooth", block: "center"});
                target.style.backgroundColor = "#ffffcc";
                setTimeout(function(){ target.style.backgroundColor = "transparent"; }, 2500);
            }
        });
        """

    cyto_html = f"""
    <div id="{container_id}" style="width: 100%; height: 550px; background: #ffffff; border-radius: 15px; border: 1px solid #eee;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{ selector: 'node', style: {{ 
                        'label': 'data(label)', 'text-valign': 'center', 'color': '#333', 
                        'background-color': 'data(color)', 'width': 65, 'height': 65,
                        'font-size': '11px', 'font-weight': 'bold', 'text-outline-width': 2,
                        'text-outline-color': '#fff', 'cursor': 'pointer'
                    }} }},
                    {{ selector: 'edge', style: {{ 
                        'width': 3, 'line-color': '#ccc', 'label': 'data(label)', 
                        'font-size': '9px', 'target-arrow-color': '#ccc', 
                        'target-arrow-shape': 'triangle', 'curve-style': 'bezier',
                        'text-rotation': 'autorotate'
                    }} }}
                ],
                layout: {{ name: 'cose', padding: 50, animate: true, nodeRepulsion: 15000 }}
            }});
            {click_js}
        }});
    </script>
    """
    components.html(cyto_html, height=580)

def fetch_author_bibliographies(author_input):
    """Zajame bibliografske podatke preko ORCID API."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    for auth in author_list:
        orcid_id = None
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers=headers, timeout=5).json()
            if s_res.get('result'): orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass
        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID: {auth.upper()} ({orcid_id}) ---\n"
                for work in works[:3]:
                    comprehensive_biblio += f"- {work.get('work-summary', [{}])[0].get('title', {}).get('title', {}).get('value', 'N/A')}\n"
            except: pass
    return comprehensive_biblio

# =========================================================
# 1. NAPREDNA ONTOLOGIJA (VSEH 12 DISCIPLIN)
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
        "Adventurers": {"description": "Explorers seeking hidden patterns."},
        "Applicators": {"description": "Pragmatic minds focused on utility."},
        "Know-it-alls": {"description": "Systemic thinkers seeking clarity."},
        "Observers": {"description": "Detached analysts monitoring systems."}
    },
    "paradigms": {
        "Empiricism": "Knowledge from sensory data.",
        "Rationalism": "Knowledge from deductive logic.",
        "Constructivism": "Knowledge as social architecture.",
        "Positivism": "Strict adherence to scientific facts.",
        "Pragmatism": "Knowledge validated by success."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing causes and effects.",
        "Principles & Relations": "Constant laws and correlations.",
        "Episodes & Sequences": "Organizing knowledge as flow.",
        "Facts & Characteristics": "Raw data and properties.",
        "Generalizations": "Universal conceptual frameworks.",
        "Glossary": "Precise terminology definitions.",
        "Concepts": "Abstract situational constructs."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation", "Experiment"], "tools": ["Particle Accelerator", "Spectrometer"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy", "Bonding"], "tools": ["NMR", "Chromatography"], "facets": ["Organic", "Electrochem"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR", "Observation"], "tools": ["Microscope", "Sequencer"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophys"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Double-Blind", "Psychometrics"], "tools": ["fMRI", "Standardized Tests"], "facets": ["Behavioral", "Cognitive"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys", "Network Analysis"], "tools": ["Data Software", "Archives"], "facets": ["Stratification", "Groups"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Formal Verification"], "tools": ["LLMGraphTransformer", "IDE", "GPU Clusters"], "facets": ["AI", "Cybersecurity"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT", "Bio-Markers"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA", "Systems Eng"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotech"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Archival Appraisal"], "tools": ["OPAC", "Metadata Schemas"], "facets": ["Information Retrieval", "Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Mapping", "Critical Analysis"], "facets": ["Epistemology", "Ethics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK"], "facets": ["Sociolinguistics", "CompLing"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE KONSTRUKCIJA
# =========================================================

# --- SESSION STATE ---
if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- STRANSKA VRSTICA (SIDEBAR) ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    # --- USER GUIDE (Klikalni gumb) ---
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    if st.session_state.show_user_guide:
        st.info("""
        1. **API Key**: First, enter your Groq API key to activate the synthesis engine.
        2. **User Profile**: Select the cognitive style that best suits your inquiry approach.
        3. **Authors**: Provide author names (e.g., Karl Petrič) to include ORCID research data.
        4. **Dimensions**: Select one or more Science Fields and Scientific Paradigms.
        5. **Inquiry**: Submit a complex, interdisciplinary problem in the large text area.
        6. **Interactive Graph**: Click nodes in the Semantic Knowledge Graph to jump to specific text locations.
        7. **Polling**: Monitor API latency and transaction status in the traffic monitor section below.
        """)
        if st.button("Close Guide ✖️"):
            st.session_state.show_user_guide = False
            st.rerun()

    if not api_key and "GROQ_API_KEY" in st.secrets: api_key = st.secrets["GROQ_API_KEY"]

    # --- TRAFFIC MONITOR (Polling/Logging) ---
    st.divider()
    st.subheader("📊 API Traffic Monitor")
    if st.session_state.traffic_log:
        for log in reversed(st.session_state.traffic_log[-5:]):
            st.caption(f"[{log['timestamp']}] {log['status']} | {log['latency']}")
    else: st.write("No traffic yet.")

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
    
    # --- SOCIAL/RESOURCES ---
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

# --- GLAVNI VMESNIK ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis engine with **Interconnected Semantic Graphs**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# Row 1: Authors (Placeholder example)
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
    st.caption("Active connectivity for real-time bibliographic synergy analysis via ORCID API.")

# Row 2: Basic config
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2:
    selected_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Computer Science", "Sociology", "Philosophy"])
with r2_c3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

# Row 3: Advanced paradigms
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1:
    selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])
with r3_c2:
    selected_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Pragmatism"])
with r3_c3:
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Educational", "Policy Making"])

# Row 4: Methods & Tools
r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1:
    selected_approaches = st.multiselect("7. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Associativity"])
agg_meth, agg_tool = [], []
for s in selected_sciences:
    agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
    agg_tool.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])
with r4_c2:
    selected_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))))
with r4_c3:
    selected_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tool))))

st.divider()
# Inquiry Placeholder example
user_query = st.text_area(
    "❓ Your Synthesis Inquiry:", 
    placeholder="Create a synergy and synthesized knowledge for better resolving global problems like crime, distress, mass migration and poverty",
    height=150
)

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Active LLMGraphTransformer)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key.")
    else:
        try:
            start_time = time.time()
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            system_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive, long-form dissertation (minimum 1200 words).
            DISCIPLINES: {", ".join(selected_sciences)}. PARADIGMS: {", ".join(selected_paradigms)}.
            RESEARCH METADATA: {biblio}.
            
            OBJECTIVE:
            Develop an exhaustive theoretical and practical synergy for the following inquiry: {user_query}.
            Structure the analysis using multi-layered causal reasoning. 

            GRAPH TASK:
            End with '### SEMANTIC_GRAPH_DATA' then a JSON block.
            MANDATORY: Connect concepts to EACH OTHER (e.g. Crime Prevention connects to Poverty Alleviation).
            JSON: {{"nodes": [{{"id": "n1", "label": "Text", "color": "#hex"}}], "edges": [{{"source": "n1", "target": "n2", "label": "rel"}}]}}
            """
            
            with st.spinner('Performing high-fidelity 12D synthesis (8–40 seconds)...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6, max_tokens=4000
                )
                
                duration = time.time() - start_time
                log_api_transaction("Success", duration)
                
                full_raw = response.choices[0].message.content
                parts = full_raw.split("### SEMANTIC_GRAPH_DATA")
                main_markdown = parts[0]
                
                # --- DVOSMERNO POVEZOVANJE (Graph to Text) ---
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            for node in graph_data.get("nodes", []):
                                label, nid = node["label"], node["id"]
                                pattern = re.compile(re.escape(label), re.IGNORECASE)
                                main_markdown = pattern.sub(f'<span id="{nid}" class="semantic-node-highlight">{label}</span>', main_markdown, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            st.subheader("🕸️ LLMGraphTransformer: Interconnected Semantic Graph")
                            st.caption("Interconnected concept network. Click nodes to jump to their primary definition in the text.")
                            
                            semantic_elements = []
                            for n in graph_data.get("nodes", []):
                                semantic_elements.append({"data": {"id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f")}})
                            for e in graph_data.get("edges", []):
                                semantic_elements.append({"data": {"source": e["source"], "target": e["target"], "label": e.get("label", "rel")}})
                            
                            render_cytoscape_network(semantic_elements, "semantic_viz", clickable=True)
                    except: st.warning("Graph parsing error.")

                st.subheader("📍 Input Synergy Map")
                input_nodes = [{"data": {"id": "q", "label": "QUERY", "color": "#e63946"}}]
                for s in selected_sciences: input_nodes.append({"data": {"id": s, "label": s, "color": "#f4a261"}})
                render_cytoscape_network(input_nodes, "input_viz")
                
                if biblio:
                    with st.expander("📚 Research Metadata"): st.text(biblio)
                
        except Exception as e:
            log_api_transaction("Failed", 0)
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v8.0 Full 12D Interconnected Dissertation Edition | 2026")
      
