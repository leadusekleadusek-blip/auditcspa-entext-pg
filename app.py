import streamlit as st
import datetime

st.set_page_config(page_title="P&G e-Work Permit", layout="wide")

st.markdown("""
<style>
    .pg-header {
        background: linear-gradient(135deg, #003366 0%, #0056b3 100%);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la Base de Données sans espaces profonds
if "permis_db" not in st.session_state:
    st.session_state.permis_db = []
    
    pt1 = {
        "id": "PT-2026-0928-01",
        "societe": "ABYLSEN",
        "pdp": "PDP-2026-042 (Bâtiment M1)",
        "n2": "Léa DUSEK",
        "zone": "Bâtiment M1 - Zone Production",
        "statut": "EN_ATTENTE_BATCH",
        "heure": "06:45",
        "derogation": True,
        "motif_derog": "Dérogation Meuleuse d'angle"
    }
    st.session_state.permis_db.append(pt1)
    
    pt2 = {
        "id": "PT-2026-0928-02",
        "societe": "APAVE",
        "pdp": "PDP-2026-104 (Tuyauterie)",
        "n2": "Marc DUPONT",
        "zone": "Bâtiment M2 - Conditionnement",
        "statut": "VALIDÉ",
        "heure": "07:15",
        "derogation": False,
        "motif_derog": "Aucune"
    }
    st.session_state.permis_db.append(pt2)

st.sidebar.title("e-Work Permit P&G")
role = st.sidebar.radio(
    "Interface :",
    ["🖥️ Borne Kiosk (EE)", "📊 Dashboard Live (DO)", "📱 Inspection (Casque Rouge)"]
)

if role == "🖥️ Borne Kiosk (EE)":
    st.markdown("<div class='pg-header'><h2>BORNE KIOSK PERMIS DE TRAVAIL</h2></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("📝 Signer un PDP", use_container_width=True)
    with col2:
        st.button("🚀 Commencer un Permis", use_container_width=True, type="primary")

    st.divider()

    col_rfid, col_form = st.columns([1, 2])
    with col_rfid:
        if st.button("💳 Simuler Badge RFID"):
            st.session_state.badge = True
            st.success("Badge Détecté : Léa DUSEK")

    val_soc = "ABYLSEN" if st.session_state.get("badge") else "ABYLSEN"
    val_n2 = "Léa DUSEK" if st.session_state.get("badge") else ""

    with col_form:
        soc = st.selectbox("Société", ["ABYLSEN", "APAVE", "AXIMA", "ENGIE"])
        pdp = st.selectbox("PDP", ["PDP-2026-042", "PDP-2026-089"])
        n2_name = st.text_input("N2", value=val_n2)

    col_loc, col_map = st.columns(2)
    with col_loc:
        zone = st.selectbox("Zone", ["Bâtiment M1", "Bâtiment M2"])
    with col_map:
        chk_meuleuse = st.checkbox("Utilisation Meuleuse d'angle")

    if st.button("🚀 SOUMETTRE LE PERMIS", type="primary"):
        nouveau_pt = {
            "id": f"PT-2026-0928-0{len(st.session_state.permis_db)+1}",
            "societe": soc,
            "pdp": pdp,
            "n2": n2_name,
            "zone": zone,
            "statut": "EN_ATTENTE_BATCH",
            "heure": datetime.datetime.now().strftime("%H:%M"),
            "derogation": chk_meuleuse,
            "motif_derog": "Dérogation Meuleuse" if chk_meuleuse else "Aucune"
        }
        st.session_state.permis_db.append(nouveau_pt)
        st.success("Permis enregistré et transmis au batch de 07h30 !")

elif role == "📊 Dashboard Live (DO)":
    st.markdown("<div class='pg-header' style='background:#1e293b;'><h2>DASHBOARD DONNEUR D'ORDRE</h2></div>", unsafe_allow_html=True)
    
    if st.button("✅ VALIDER TOUT LE BATCH (07h30)", type="primary"):
        for p in st.session_state.permis_db:
            p["statut"] = "VALIDÉ"
        st.success("Batch validé !")
        
    st.dataframe(st.session_state.permis_db, use_container_width=True)

else:
    st.markdown("<div class='pg-header' style='background:#b91c1c;'><h2>AUDIT TERRAIN QR CODE</h2></div>", unsafe_allow_html=True)
    
    pt_select = st.selectbox("Permis à scanner :", [p["id"] for p in st.session_state.permis_db])
    if st.button("🔍 Scanner", type="primary"):
        scanned = next(p for p in st.session_state.permis_db if p["id"] == pt_select)
        st.json(scanned)
