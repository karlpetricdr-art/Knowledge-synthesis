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
# 0. KONFIGURACIJA IN NAPREDNI STILI (CSS)
# =========================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Integracija CSS za vizualne poudarke, Google linke in gladko navigacijo
st.markdown("""
<style>
    .semantic-node-highlight {
        color: #2a9d8f;
        font-weight: bold;
        border-bottom: 2px solid #2a9d8f;
        padding: 0 2px;
        background-color: #f0fdfa;
        border-radius: 4px;
        transition: all 0.3s ease;
        text-decoration: none !important;
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1;
        color: #264653;
        border-bottom: 2px solid #e76f51;
    }
    .google-icon {
        font-size: 0.7em;
        vertical-align: super;
        margin-left: 2px;
        color: #457b9d;
        opacity: 0.7;
    }
    .stMarkdown {
        line-height: 1.7;
        font-size: 1.05em;
    }
    #cy-container {
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-radius: 15px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Pretvori SVG v base64 format za varno vstavljanje v HTML."""
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

# --- CYTOSCAPE RENDERER Z HIERARHIJO IN NAVIGACIJO ---
def render_cytoscape_network(elements, container_id="cy"):
    """
    Izriše interaktivno omrežje z napredno vizualno hierarhijo.
    Root vozlišča so največja (85px), Branch srednja (60px), Leaf pa najmanjša (40px).
    Vključuje JS za skok na tekst v starševskem oknu.
    """
    cyto_html = f"""
    <div id="{container_id}" style="width: 100%; height: 550px; background: #ffffff; border: 1px solid #eee;"></div>
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
                            'width': 'data(size)',
                            'height': 'data(size)',
                            'font-size': '11px',
                            'font-weight': 'bold',
                            'text-outline-width': 2,
                            'text-outline-color': '#fff',
                            'cursor': 'pointer',
                            'z-index': 'data(z_index)'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 2,
                            'line-color': '#ced4da',
                            'label': 'data(label)',
                            'font-size': '9px',
                            'color': '#495057',
                            'target-arrow-color': '#ced4da',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'text-rotation': 'autorotate'
                        }}
                    }}
                ],
                layout: {{ name: 'cose', padding: 50, animate: true, nodeRepulsion: 18000 }}
            }});
            
            cy.on('tap', 'node', function(evt){{
                var elementId = evt.target.id();
                var target = window.parent.document.getElementById(elementId);
                if (target) {{
                    target.scrollIntoView({{behavior: "smooth", block: "center"}});
                    target.style.backgroundColor = "#ffffcc";
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 2500);
                }}
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=580)

# --- PRIDOBIVANJE BIBLIOGRAFIJ Z LETNICAMI ---
def fetch_author_bibliographies(author_input):
    """Zajame bibliografske podatke z letnicami preko ORCID in Scholar API baz."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers=headers, timeout=6).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass

        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=6).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID BIBLIOGRAPHY: {auth.upper()} ({orcid_id}) ---\n"
                if works:
                    for work in works[:5]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                        pub_date = summary.get('publication-date')
                        year = pub_date.get('year').get('value', 'n.d.') if pub_date and pub_date.get('year') else "n.d."
                        comprehensive_biblio += f"- [{year}] {title}\n"
                else: comprehensive_biblio += "No public works found.\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=3&fields=title,year"
                ss_res = requests.get(ss_url, timeout=6).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR BIBLIOGRAPHY: {auth.upper()} ---\n"
                    for p in papers:
                        comprehensive_biblio += f"- [{p.get('year','n.d.')}] {p['title']}\n"
            except: pass
    return comprehensive_biblio

# =========================================================
# 1. POPOLNA MULTIDIMENZIONALNA ONTOLOGIJA (VSEH 12 DISCIPLIN)
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
        "Adventurers": {"description": "Explorers of hidden patterns and new horizons."},
        "Applicators": {"description": "Pragmatic minds focused on utility and efficiency."},
        "Know-it-alls": {"description": "Systemic thinkers seeking absolute conceptual clarity."},
        "Observers": {"description": "Detached analysts who monitor system evolution."}
    },
    "paradigms": {
        "Empiricism": "Knowledge based on sensory experience and induction.",
        "Rationalism": "Knowledge based on deductive logic and innate principles.",
        "Constructivism": "Knowledge as a social and cognitive construction.",
        "Positivism": "Strict adherence to verifiable scientific facts.",
        "Pragmatism": "Knowledge validated by its practical success and utility."
    },
    "knowledge_models": {
        "Causal Connections": "Analyzing deep causes, effects, and the 'why'.",
        "Principles & Relations": "Constant laws and fundamental correlations.",
        "Episodes & Sequences": "Organizing knowledge as a chronological flow.",
        "Facts & Characteristics": "Raw data and properties of objects or events.",
        "Generalizations": "Broad, universal conceptual frameworks.",
        "Glossary": "Precise definitions of terminology.",
        "Concepts": "Abstract mental constructs and situational situational maps."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation"], "tools": ["Accelerator", "Spectrometer"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Chromatography"], "facets": ["Organic", "Molecular"]},
        "Biology": {"cat": "Natural", "methods": ["DNA Sequencing", "CRISPR"], "tools": ["Microscope", "Bio-Incubator"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophys"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Double-Blind", "Psychometrics"], "tools": ["fMRI", "Testing Kits"], "facets": ["Behavioral", "Cognitive"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics", "Archives"], "facets": ["Stratification", "Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Formal Verification"], "tools": ["LLMGraphTransformer", "GPU Clusters"], "facets": ["AI", "Cybersecurity"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT", "Bio-Markers"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotech"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Archival Appraisal"], "tools": ["OPAC", "Metadata Schemas"], "facets": ["Retrieval", "Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Mapping", "Critical Text Analysis"], "facets": ["Epistemology", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK Toolkit"], "facets": ["Socioling", "CompLing"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE KONSTRUKCIJA
# =========================================================

# Inicializacija session_state
if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- STRANSKA VRSTICA (SIDEBAR) ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    # --- USER GUIDE (Klikalni gumb pod API poljem) ---
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    if st.session_state.show_user_guide:
        st.info("""
        1. **API Key**: Enter your Groq API key to connect the AI engine.
        2. **User Profile**: Choose a cognitive thinking style (e.g., Adventurer).
        3. **Authors**: Provide author names for real-time bibliographic data integration.
        4. **Select Sciences**: Choose from 12 fields to create interdisciplinary synergy.
        5. **Submit Inquiry**: Ask a complex question about global issues or science.
        6. **Search Links**: Click pojme in the text to perform a direct Google Search.
        7. **Semantic Graph**: Click nodes to scroll to their precise definition in the text.
        """)
        if st.button("Close Guide ✖️"): st.session_state.show_user_guide = False; st.rerun()

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
    
    # Gumbi za zunanje vire
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

# --- GLAVNI VMESNIK ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Hierarchical & Associative Semantic Linking**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# ROW 1: AUTHORS
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
    st.caption("Active connectivity for real-time bibliographic analysis (includes publication years).")

# ROW 2: CORE CONFIG
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    sel_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2:
    sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Computer Science", "Sociology", "Philosophy"])
with r2_c3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

# ROW 3: PARADIGMS & MODELS
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1:
    sel_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])
with r3_c2:
    sel_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Pragmatism"])
with r3_c3:
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making"])

# ROW 4: METHODS & TOOLS
r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1:
    sel_approaches = st.multiselect("7. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Associativity"])

agg_meth, agg_tool = [], []
for s in sel_sciences:
    if s in KNOWLEDGE_BASE["subject_details"]:
        agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
        agg_tool.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

with r4_c2:
    sel_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))))
with r4_c3:
    sel_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tool))))

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", 
                         placeholder="Create a synergy and synthesized knowledge for better resolving global problems like crime, distress, mass migration and poverty",
                         height=150)

# =========================================================
# 3. JEDRO SINTEZE: GROQ AI + HIERARCHICAL MAPPING
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key.")
    elif not user_query: st.warning("Please enter your inquiry.")
    else:
        try:
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # SISTEMSKO NAVODILO: Fokus na obširnost, hierarhijo in asociativnost
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive dissertation (1200+ words).
            DISCIPLINES: {", ".join(sel_sciences)}. CONTEXT AUTHORS: {biblio}.
            
            HIERARCHY & ASSOCIATIVITY TASK:
            1. Analyze the inquiry ({user_query}) through hierarchical layers (Root concepts down to Leaf details).
            2. Establish associative links between disparate disciplines (e.g. Neuroscience combined with Policy Making).
            
            LLMGraphTransformer TASK:
            End with '### SEMANTIC_GRAPH_JSON' followed by a JSON block.
            MANDATORY: Define 'type' as 'Root', 'Branch', or 'Leaf' for each node.
            JSON: {{"nodes": [{{"id": "n1", "label": "Label", "type": "Root|Branch|Leaf", "color": "#hex"}}], "edges": [{{"source": "n1", "target": "n2", "label": "link"}}]}}
            """
            
            with st.spinner('Synthesizing exhaustive hierarchical synergy (8–40s)...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6, max_tokens=4000
                )
                
                full_raw = response.choices[0].message.content
                parts = full_raw.split("### SEMANTIC_GRAPH_JSON")
                text_out = parts[0]
                
                # --- PROCESIRANJE BESEDILA (Google Search + ID Anchors) ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        for n in g_json.get("nodes", []):
                            lbl, nid = n["label"], n["id"]
                            g_url = urllib.parse.quote(lbl)
                            pattern = re.compile(re.escape(lbl), re.IGNORECASE)
                            # Zamenja tekst z Google Search povezavo in ID značko
                            replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                            text_out = pattern.sub(replacement, text_out, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(text_out, unsafe_allow_html=True)

                # --- VIZUALIZACIJA (Hierarchical Graph) ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        st.subheader("🕸️ LLMGraphTransformer: Hierarchical Associative Map")
                        st.caption("Root nodes are larger. Click text concepts to perform a Google Search. Click nodes to jump to text.")
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            level = n.get("type", "Branch")
                            size = 85 if level == "Root" else (60 if level == "Branch" else 40)
                            z_idx = 10 if level == "Root" else 1
                            elements.append({"data": {
                                "id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f"),
                                "size": size, "z_index": z_idx
                            }})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {
                                "source": e["source"], "target": e["target"], "label": e.get("label", "associates")
                            }})
                        render_cytoscape_network(elements, "semantic_viz_hier")
                    except: st.warning("Graph parsing skipped.")

                if biblio:
                    with st.expander("📚 View Metadata Fetched from Research Databases"):
                        st.text(biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v8.8 Hierarchical & Associative Edition | 2026")


