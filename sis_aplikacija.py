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

# --- CYTOSCAPE RENDERER Z DVOSMERNO NAVIGACIJO ---
def render_cytoscape_network(elements, container_id="cy", clickable=False):
    """Izriše interaktivno omrežje Cytoscape.js z scroll-to-text funkcionalnostjo."""
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
                    'label': 'data(label)', 'text-valign': 'center', 'color': '#333', 
                    'background-color': 'data(color)', 'width': 60, 'height': 60,
                    'font-size': '11px', 'font-weight': 'bold', 'text-outline-width': 2,
                    'text-outline-color': '#fff', 'cursor': 'pointer'
                }} }},
                {{ selector: 'edge', style: {{ 
                    'width': 3, 'line-color': '#ccc', 'label': 'data(label)', 
                    'font-size': '9px', 'target-arrow-color': '#ccc', 
                    'target-arrow-shape': 'triangle', 'curve-style': 'bezier' 
                }} }}
            ],
            layout: {{ name: 'cose', padding: 40, animate: true }}
        }});
        {click_js}
    </script>
    """
    components.html(cyto_html, height=520)

def fetch_author_bibliographies(author_input):
    """Pridobi bibliografske podatke preko ORCID in Semantic Scholar."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    for auth in author_list:
        orcid_id = None
        if len(auth) == 19 and auth.count('-') == 3: orcid_id = auth
        else:
            try:
                search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
                s_res = requests.get(search_url, headers=headers, timeout=8).json()
                if s_res.get('result'): orcid_id = s_res['result'][0]['orcid-identifier']['path']
            except: pass
        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=8).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID BIBLIOGRAPHY: {auth.upper()} ({orcid_id}) ---\n"
                if works:
                    for work in works[:5]:
                        comprehensive_biblio += f"- {work.get('work-summary', [{}])[0].get('title', {}).get('title', {}).get('value', 'N/A')}\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=3&fields=title"
                ss_res = requests.get(ss_url, timeout=8).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR BIBLIOGRAPHY: {auth.upper()} ---\n"
                    for p in papers: comprehensive_biblio += f"- {p['title']}\n"
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
    "paradigms": {"Empiricism": "Sensory data.", "Rationalism": "Logic.", "Constructivism": "Socially constructed.", "Positivism": "Facts.", "Pragmatism": "Practical utility."},
    "knowledge_models": {"Causal Connections": "Why/How.", "Principles & Relations": "Laws.", "Episodes & Sequences": "Time.", "Facts & Characteristics": "Data.", "Generalizations": "Frameworks.", "Glossary": "Terms.", "Concepts": "Abstract."},
    "subject_details": {
        "Physics": {"methods": ["Mathematical Modeling", "Simulation"], "tools": ["Spectrometer"], "facets": ["Quantum Mechanics", "Relativity"]},
        "Chemistry": {"methods": ["Synthesis"], "tools": ["NMR"], "facets": ["Organic Chemistry"]},
        "Biology": {"methods": ["Sequencing"], "tools": ["Microscope"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"methods": ["Neuroimaging"], "tools": ["fMRI"], "facets": ["Neuroplasticity"]},
        "Psychology": {"methods": ["Psychometrics"], "tools": ["Standardized Tests"], "facets": ["Cognitive Behavior"]},
        "Sociology": {"methods": ["Ethnography"], "tools": ["Data Software"], "facets": ["Stratification"]},
        "Computer Science": {"methods": ["Algorithm Design"], "tools": ["LLM + LangChain + LLMGraphTransformer", "Markmap"], "facets": ["Knowledge Graphs"]},
        "Medicine": {"methods": ["Clinical Trials"], "tools": ["MRI/CT"], "facets": ["Immunology"]},
        "Engineering": {"methods": ["FEA"], "tools": ["3D Printers"], "facets": ["Robotics"]},
        "Library Science": {"methods": ["Taxonomy"], "tools": ["OPAC"], "facets": ["Metadata Retrieval"]},
        "Philosophy": {"methods": ["Socratic Method"], "tools": ["Logic Tools"], "facets": ["Epistemology"]},
        "Linguistics": {"methods": ["Corpus Analysis"], "tools": ["NLTK"], "facets": ["Computational Linguistics"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE
# =========================================================
st.set_page_config(page_title="SIS Synthesizer", page_icon="🌳", layout="wide")

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Intermediate"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis engine with **Duo-directional Semantic Linking**.")

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
        1. **API Key**: Enter key for Groq LLM.
        2. **User Profile**: Select thinking style.
        3. **Authors**: Use 'Karl Petrič, Samo Kralj, Teodor Petrič'.
        4. **Execute**: Long-form synthesis with clickable Graph nodes.
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
    if st.button("♻️ Reset Session", use_container_width=True): st.session_state.clear(); st.rerun()
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

# --- CONFIGURE INTERFACE ---
st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: selected_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2: selected_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Computer Science", "Sociology", "Philosophy"])
with r2_c3: expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1: selected_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])
with r3_c2: selected_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism", "Pragmatism"])
with r3_c3: goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", 
                         placeholder="Create a synergy and synthesized knowledge for better resolving global problems like crime, distress, mass migration and poverty")

# =========================================================
# 3. CORE SYNTHESIS LOGIC (Active LLMGraphTransformer)
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing API Key.")
    else:
        try:
            synergy_biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # Anchor za povrat na graf
            st.markdown('<div id="top_graph_anchor"></div>', unsafe_allow_html=True)
            
            system_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive interdisciplinary dissertation (1200+ words).
            Integrate: {", ".join(selected_sciences)}. Use Authors metadata: {synergy_biblio}.
            
            STRUCTURE:
            - Deep theoretical framework.
            - Practical interdisciplinary synergy for global issues (crime, poverty, etc).
            - Use clearly defined concepts.

            JSON TASK:
            End with '### SEMANTIC_GRAPH_JSON' then a JSON block with "nodes" and "edges".
            """
            
            with st.spinner('Synthesizing exhaustive research synergy...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6,
                    max_tokens=4000
                )
                
                full_raw = response.choices[0].message.content
                parts = full_raw.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- BI-DIRECTIONAL LINKING LOGIC ---
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            for node in graph_data.get("nodes", []):
                                label, nid = node["label"], node["id"]
                                # Zamenjaj prvo pojavitev s span-om in povratnim linkom [↑]
                                pattern = re.compile(re.escape(label), re.IGNORECASE)
                                replacement = f'<span id="{nid}" style="color:#2a9d8f; font-weight:bold; border-bottom:1px dashed #2a9d8f;">{label} <a href="#top_graph_anchor" style="text-decoration:none; font-size:10px;">[↑]</a></span>'
                                main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            graph_data = json.loads(json_match.group())
                            st.subheader("🕸️ Semantic Knowledge Graph")
                            st.caption("Click nodes to scroll to text definition. Click [↑] in text to return here.")
                            
                            semantic_elements = []
                            for n in graph_data.get("nodes", []):
                                semantic_elements.append({"data": {"id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f")}})
                            for e in graph_data.get("edges", []):
                                semantic_elements.append({"data": {"source": e["source"], "target": e["target"], "label": e.get("label", "rel")}})
                            
                            render_cytoscape_network(semantic_elements, "semantic_viz", clickable=True)
                    except: st.warning("Graph error.")

                st.subheader("📍 Structural Configuration Map")
                input_nodes = [{"data": {"id": "q", "label": "INQUIRY", "color": "#e63946"}}]
                input_edges = []
                for s in selected_sciences:
                    input_nodes.append({"data": {"id": s, "label": s, "color": "#f4a261"}})
                    input_edges.append({"data": {"source": "q", "target": s}})
                render_cytoscape_network(input_nodes + input_edges, "input_viz")
                
                if synergy_biblio:
                    with st.expander("📚 Metadata"): st.text(synergy_biblio)
                
        except Exception as e: st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Synthesizer v6.5 | Full 12D Interactive Semantic Edition | 2026")
