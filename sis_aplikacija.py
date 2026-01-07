import streamlit as st
import json
from openai import OpenAI

# =========================================================
# 1. VAŠA LEGO ONTOLOGIJA (Podatki iz slike in besedila)
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
            "opis": "Usmerjeni v reševanje konkretnih stanj in uporabo modelov (npr. obvladovanje stresa)."
        }
    },
    "podrobnosti_predmetov": {
        "psihologija": {
            "kljucni_pojmi": ["stres", "evstres", "distres", "stresni dejavniki", "psihološki vzgibi"],
            "program_tip": "izbirni / izobraževalna zanimanja",
            "klasifikacija": "CC 372 / Modeli (teoretični)"
        },
        "zgodovina": {
            "kljucni_pojmi": ["prazgodovina", "stari vek", "srednji vek", "novi vek"],
            "program_tip": "izbirni / zasebna zanimanja",
            "klasifikacija": "Pustolovci / DE:zgodovina"
        },
        "glasba": {
            "kljucni_pojmi": ["takt", "ritem", "zvok", "melodija"],
            "program_tip": "osnovni program (dejavnosti 987) / izbirni",
            "klasifikacija": "Pustolovci / DE:glasba"
        },
        "geografija": {
            "kljucni_pojmi": ["hierarhija", "miselne silnice", "prostor"],
            "program_tip": "osnovni program / izbirni",
            "klasifikacija": "Pustolovci / DE:geografija"
        }
    }
}

# =========================================================
# 2. NASTAVITVE SPLETNEGA VMESNIKA (Streamlit)
# =========================================================
st.set_page_config(page_title="SIS Sinteznik Znanja", page_icon="🧱", layout="centered")

st.title("🧱 SIS - Sinteznik interesnih sfer")
st.write("Specializiran model za sintezo znanja na podlagi vaše Lego taksonomije.")

# Stranska vrstica za ključ in pregled baze
with st.sidebar:
    st.header("Nastavitve")
    api_key = st.text_input("Vnesite OpenAI API ključ:", type="password")
    st.divider()
    st.subheader("Pregled baze znanja")
    if st.checkbox("Prikaži JSON strukturo"):
        st.json(BAZA_ZNANJA)
    st.info("Sistem uporablja vaše specifične profile (Pustolovci, Aplikativci) za generiranje odgovorov.")

# Glavni vnosni obrazec
st.divider()
col1, col2 = st.columns(2)

with col1:
    profil = st.radio("Izberite profil:", ["Pustolovci", "Aplikativci"])
with col2:
    predmet = st.selectbox("Izberite predmet:", list(BAZA_ZNANJA["podrobnosti_predmetov"].keys()))

vprasanje = st.text_input("Vprašanje za AI (npr. Kako ta predmet vpliva na moj profil?):")

# =========================================================
# 3. LOGIKA ZA SINTEZO (AI Procesiranje)
# =========================================================
if st.button("Zaženi sintezo znanja"):
    if not api_key:
        st.warning("Prosim, vnesite OpenAI API ključ v stranski vrstici.")
    elif not vprasanje:
        st.warning("Prosim, vnesite vprašanje.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # Priprava konteksta iz vaše baze
            kontekst_json = json.dumps(BAZA_ZNANJA, ensure_ascii=False)
            
            system_prompt = f"""
            Si specializiran model 'SIS Sinteznik'. Tvoja naloga je svetovati uporabniku na podlagi te baze:
            {kontekst_json}
            
            Pravila:
            1. Vedno poveži uporabnikov profil (npr. {profil}) s predmetom (npr. {predmet}).
            2. Uporabi točne pojme iz baze (npr. če je predmet psihologija, omenjaj evstres/distres).
            3. Odgovor naj bo strukturiran kot 'Sinteza znanja' po vašem Lego načrtu.
            """
            
            with st.spinner('AI sintetizira podatke po vaši strukturi...'):
                komunikacija = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Profil: {profil}, Predmet: {predmet}. Vprašanje: {vprasanje}"}
                    ],
                    temperature=0.5
                )
                
                odgovor = komunikacija.choices[0].message.content
                
                # Prikaz rezultata
                st.success("Rezultat sinteze:")
                st.markdown(odgovor)
                
                # Dodaten izpis iz baze za preverjanje
                with st.expander("Uporabljeni podatki iz vaše baze:"):
                    st.write(f"**Profil:** {profil}")
                    st.write(f"**Vzgibi:** {BAZA_ZNANJA['profili']['DE:' + profil.lower()]['vzgibi']}")
                    st.write(f"**Pojmi:** {BAZA_ZNANJA['podrobnosti_predmetov'][predmet]['kljucni_pojmi']}")

        except Exception as e:
            st.error(f"Napaka pri povezavi z AI: {e}")

st.divider()
st.caption("SIS Model | Temelji na Lego arhitekturi znanja | 2024")