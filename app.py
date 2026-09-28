import datetime
import streamlit as st

st.set_page_config(page_title="P&G Amiens - e-Work Permit System", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .pg-header {
        background: linear-gradient(135deg, #003366 0%, #0056b3 100%);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

if "permis_db" not in st.session_state:
    st.session_state.permis_db = []
    p1 = {"id": "PT-2026-0928-01", "societe": "ABYLSEN", "pdp": "PDP-2026-042", "mop": "MoP-01", "n2": "Léa DUSEK", "tel_n2": "06 12 34 56 78", "zone": "Bâtiment M1 - Zone Production", "statut": "EN_ATTENTE_BATCH", "heure": "06:45", "derogations": ["Meuleuse d angle"], "permis_specifiques": []}
    p2 = {"id": "PT-2026-0928-02", "societe": "APAVE", "pdp": "PDP-2026-104", "mop": "MoP-01", "n2": "Marc DUPONT", "tel_n2": "06 98 76 54 32", "zone": "Bâtiment M2 - Conditionnement", "statut": "VALIDÉ", "heure": "07:15", "derogations": [], "permis_specifiques": ["Consignation (LOTO)"]}
    st.session_state.permis_db.extend([p1, p2])

db_pdps = {"ABYLSEN": ["PDP-2026-042", "PDP-2026-089"], "APAVE": ["PDP-2026-104"]}
db_zones = {"Bâtiment M1 - Zone Production": {"pr": "PR-2", "confinement": "ZC-01", "urg": "03.22.54.33.33"}, "Bâtiment M2 - Conditionnement": {"pr": "PR-4", "confinement": "ZC-03", "urg": "03.22.54.33.34"}}

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Procter_%26_Gamble_logo.svg/1024px-Procter_%26_Gamble_logo.svg.png", width=80)
st.sidebar.title("e-Work Permit P&G")
role = st.sidebar.radio("Interface :", ["🖥️ Borne Kiosk (EE)", "📊 Dashboard Live (DO)", "📱 Inspection Terrain (Casque Rouge)"])

if role == "🖥️ Borne Kiosk (EE)":
    st.markdown("<div class='pg-header'><h2>BORNE KIOSK PERMIS DE TRAVAIL</h2></div>", unsafe_allow_html=True)
    tab = st.radio("Parcours :", ["🚀 PERMIS DE TRAVAIL", "📝 ÉMARGEMENT PDP"], horizontal=True)
    if tab == "📝 ÉMARGEMENT PDP":
        soc = st.selectbox("Société", list(db_pdps.keys()))
        nom = st.text_input("Nom & Prénom")
        statut = st.selectbox("Statut", ["N1 (Compagnon)", "N2 (Responsable)"])
        tel = st.text_input("Téléphone N2") if "N2" in statut else ""
        if st.button("✅ VALIDER ÉMARGEMENT PDP", type="primary"):
            st.success(f"Émargement validé pour {nom}")
    else:
        if st.button("💳 Simuler Badge RFID"):
            st.session_state.badge = True
            st.success("Badge Détecté : Léa DUSEK (ABYLSEN)")
        soc = st.selectbox("Société", list(db_pdps.keys()))
        zone = st.selectbox("Zone", list(db_zones.keys()))
        chk_meuleuse = st.checkbox("Dérogation Meuleuse d angle")
        if st.button("🚀 SOUMETTRE LE PERMIS", type="primary"):
            nouveau = {"id": f"PT-2026-0928-0{len(st.session_state.permis_db)+1}", "societe": soc, "pdp": "PDP-2026-042", "mop": "MoP-01", "n2": "Léa DUSEK", "tel_n2": "0612345678", "zone": zone, "statut": "EN_ATTENTE_BATCH", "heure": datetime.datetime.now().strftime("%H:%M"), "derogations": ["Meuleuse d angle"] if chk_meuleuse else [], "permis_specifiques": []}
            st.session_state.permis_db.append(nouveau)
            st.success("Permis enregistré !")

elif role == "📊 Dashboard Live (DO)":
    st.markdown("<div class='pg-header'><h2>DASHBOARD DONNEUR D'ORDRE</h2></div>", unsafe_allow_html=True)
    if st.button("✅ VALIDER LE BATCH (07h30)", type="primary"):
        for p in st.session_state.permis_db: p["statut"] = "VALIDÉ"
        st.success("Batch 07h30 validé !")
    st.dataframe(st.session_state.permis_db, use_container_width=True)

else:
    st.markdown("<div class='pg-header'><h2>INSPECTION QR CODE</h2></div>", unsafe_allow_html=True)
    pt_sel = st.selectbox("Permis :", [p["id"] for p in st.session_state.permis_db])
    if st.button("🔍 Scan QR Code", type="primary"):
        st.json(next(p for p in st.session_state.permis_db if p["id"] == pt_sel))
