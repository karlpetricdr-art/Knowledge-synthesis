import streamlit as st
import json
from openai import OpenAI

# =========================================================
# 1. VAŠA LEGO ONTOLOGIJA (Vsi podatki iz slike in besedila)
# =========================================================
BAZA_ZNANJA = {
    "profili": {
        "DE:pustolovci": {
            "predmeti": ["geografija", "glasba", "zgodovina"],
            "vzgibi": "miselne silnice",
            "opis": "Usmerjeni v raziskovanje širših sistemov in hierarhije misli."
        },
        "DE:aplikativci": {
            "predmeti": ["psihologija"],
            "vzgibi": "psihološki vzgibi",
            "opis": "Usmerjeni v reševanje konkretnih stanj (npr. obvladovanje stresa)."
        }
    },
    "podrobnosti_predmetov": {
        "psihologija": {
            "kljucni_pojmi": ["stres", "evstres", "distres", "stresni dejavniki"],
            "program_tip": "izbirni / izobraževalna zanimanja"
        },
        "zgodovina": {
            "kljucni_pojmi": ["prazgodovina", "stari vek", "srednji vek", "novi vek"],
            "program_tip": "izbirni / zasebna zanimanja"
        },
        "glasba": {
            "kljucni_pojmi": ["takt", "ritem", "zvok", "melodija"],
            "program_tip": "osnovni program (dejavnosti 987) / izbirni"
        },
        "geografija": {
            "kljucni_pojmi": ["hierarhija", "miselne silnice", "prostor"],
            "program_tip": "osnovni program / izbirni"
        }
    }
}

# =========================================================
# 2. VMESNIK (Streamlit)
# =========================================================
st.set_page_config(page_title="SIS Groq Sinteznik", page_icon="🧱")

st.title("🧱 SIS - Sinteznik znanja (Groq AI)")
st.markdown("Model za sintezo znanja po vaši Lego taksonomiji.")

with st.sidebar:
    st.header("Nastavitve")
    # Preverimo, če je ključ v Secrets (pod imenom OPENAI_API_KEY)
    api_key = st.text_input("Vnesite Groq API ključ (gsk_...):", type="password")
    
    if not api_key and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    
    st.divider()
    if st.checkbox("Prikaži Lego bazo"):
        st.json(BAZA_ZNANJA)

# Izbira parametrov
col1, col2 = st.columns(2)
with col1:
    profil = st.radio("Izberite profil:", ["Pustolovci", "Aplikativci"])
with col2:
    predmet = st.selectbox("Izberite predmet:", list(BAZA_ZNANJA["podrobnosti_predmetov"].keys()))

vprasanje = st.text_input("Vprašanje za sintezo:", placeholder="Npr. Poveži ritem z mojim profilom...")

# =========================================================
# 3. LOGIKA ZA GROQ AI
# =========================================================
if st.button("Sintetiziraj z Groq AI"):
    if not api_key:
        st.error("Napaka: Manjka API ključ! Vnesite ga v nastavitve.")
    else:
        try:
            # POVEZAVA NA GROQ (Uporabljamo OpenAI knjižnico s preusmeritvijo)
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            
            kontekst = json.dumps(BAZA_ZNANJA, ensure_ascii=False)
            
            system_msg = f"""
            Si SIS Sinteznik. Tvoji odgovori temeljijo na tej bazi: {kontekst}.
            Uporabi strokovne pojme iz baze (npr. miselne silnice, evstres).
            Pojasni, kako se izbrani predmet povezuje s profilom uporabnika.
            """
            
            with st.spinner('Groq razmišlja...'):
                odgovor = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": f"Profil: {profil}, Predmet: {predmet}. Vprašanje: {vprasanje}"}
                    ],
                    temperature=0.5
                )
                
                st.success("Rezultat sinteze:")
                st.write(odgovor.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Prišlo je do napake pri povezavi: {e}")

st.divider()
st.caption("SIS Model | Brezplačni Groq pogon | 2024")
