import streamlit as st
import datetime

st.set_page_config(
    page_title="P&G Amiens — e-Work Permit System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .pg-header {
        background: linear-gradient(135deg, #003366 0%, #0056b3 100%);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
    .stButton>button { border-radius: 6px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if "permis_db" not in st.session_state:
    st.session_state.permis_db = [
        {
            "id": "PT-2026-0928-01",
            "societe": "ABYLSEN",
            "pdp": "PDP-2026-042 (Bâtiment M1 - Rénovation)",
            "mop": "MoP-01: Peinture & Finitions M1",
            "n2": "Léa DUSEK",
            "statut_n2": "N2 (Responsable)",
            "tel_n2": "06 12 34 56 78",
            "zone": "Bâtiment M1 - Zone Production",
            "emplacement": "1er étage, Bureau 104",
            "pr": "PR-2 (Parking Ouest)",
            "confinement": "ZC-01 (Hall M1)",
            "urg": "03.22.54.33.33",
            "mode_envoi": "programmé",
            "statut": "EN_ATTENTE_BATCH",
            "heure": "06:45",
            "produits": "Acétone / Solvant peinture",
            "epis": ["Chaussures EN 20345", "Casque + Jugulaire", "Lunettes EN 166", "Gilet Visibilité", "Gants Anti-coupure"],
            "permis_specifiques": [],
            "derogations": ["Meuleuse d'angle"],
            "compagnons": ["Léa DUSEK (N2)", "Matthieu MARTIN (N1)"]
        },
        {
            "id": "PT-2026-0928-02",
            "societe": "APAVE",
            "pdp": "PDP-2026-104 (Inspection Pression)",
            "mop": "MoP-01: Épreuve Hydraulique Tuyauterie",
            "n2": "Marc DUPONT",
            "statut_n2": "N2 (Responsable)",
            "tel_n2": "06 98 76 54 32",
            "zone": "Bâtiment M2 - Conditionnement",
            "emplacement": "Ligne de conditionnement 3",
            "pr": "PR-4 (Zone Nord)",
            "confinement": "ZC-03 (Atrium M2)",
            "urg": "03.22.54.33.34",
            "mode_envoi": "immédiat",
            "statut": "VALIDÉ",
            "heure": "07:15",
            "produits": "Eau sous pression",
            "epis": ["Chaussures EN 20345", "Casque + Jugulaire", "Lunettes EN 166", "Gilet Visibilité", "Gants Anti-coupure", "Bouchons d'oreilles"],
            "permis_specifiques": ["Consignation (LOTO)"],
            "derogations": [],
            "compagnons": ["Marc DUPONT (N2)"]
        }
    ]

db_pdps = {
    "ABYLSEN": ["PDP-2026-042 (Bâtiment M1 - Rénovation)", "PDP-2026-089 (Conditionnement)"],
    "APAVE": ["PDP-2026-104 (Inspection Pression)", "PDP-2026-112 (Conformité Électrique)"],
    "AXIMA": ["PDP-2026-015 (HVAC Zone Production)"],
    "ENGIE": ["PDP-2026-067 (Chaufferie Vapeur)"]
}

db_mops = {
    "PDP-2026-042 (Bâtiment M1 - Rénovation)": ["MoP-01: Peinture & Finitions M1", "MoP-02: Remplacement Cloisons"],
    "PDP-2026-089 (Conditionnement)": ["MoP-01: Maintenance Ligne 3"],
    "PDP-2026-104 (Inspection Pression)": ["MoP-01: Épreuve Hydraulique Tuyauterie"],
    "PDP-2026-112 (Conformité Électrique)": ["MoP-01: Audit Armoires TGBT"],
    "PDP-2026-015 (HVAC Zone Production)": ["MoP-01: Nettoyage Filtres CTA"],
    "PDP-2026-067 (Chaufferie Vapeur)": ["MoP-01: Isoler Purgeur Vapeur"]
}

db_zones = {
    "Bâtiment M1 - Zone Production": {"pr": "PR-2 (Parking Ouest)", "confinement": "ZC-01 (Hall M1)", "urg": "03.22.54.33.33"},
    "Bâtiment M1 - Bureaux": {"pr": "PR-2 (Parking Ouest)", "confinement": "ZC-01 (Hall M1)", "urg": "03.22.54.30.00"},
    "Bâtiment M2 - Conditionnement": {"pr": "PR-4 (Zone Nord)", "confinement": "ZC-03 (Atrium M2)", "urg": "03.22.54.33.34"},
    "Zone Extérieure / Logistique": {"pr": "PR-1 (Entrée Principale)", "confinement": "ZC-00 (Poste Central)", "urg": "03.22.54.33.33"}
}

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Procter_%26_Gamble_logo.svg/1024px-Procter_%26_Gamble_logo.svg.png", width=80)
st.sidebar.title("e-Work Permit P&G")
st.sidebar.caption("Site d'Amiens — Solution Unifiée")

role = st.sidebar.radio(
    "Choisir l'interface à démontrer :",
    [
        "🖥️ Borne Kiosk (Intervenant EE)",
        "📊 Dashboard Live & Batch 07h30 (DO / HSE)",
        "📱 Inspection Terrain QR Code (Casque Rouge)"
    ]
)

if role == "🖥️ Borne Kiosk (Intervenant EE)":
    st.markdown("""
    <div class="pg-header">
        <h2 style='margin:0;'>PROCTER & GAMBLE — BORNE KIOSK PERMIS DE TRAVAIL</h2>
        <p style='margin:0; opacity:0.8;'>Accueil Sécurité & Émission Numérique des Permis (STA)</p>
    </div>
    """, unsafe_allow_html=True)

    tab_choice = st.radio("Sélectionnez votre parcours :", ["🚀 COMMENCER UN PERMIS DE TRAVAIL", "📝 SIGNER UN PLAN DE PRÉVENTION (ÉMARGEMENT PDP)"], horizontal=True)
    st.divider()

    if tab_choice == "📝 SIGNER UN PLAN DE PRÉVENTION (ÉMARGEMENT PDP)":
        st.subheader("📝 Émargement d'un Plan de Prévention (PDP)")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            soc_pdp = st.selectbox("Entreprise Extérieure", list(db_pdps.keys()), key="pdp_soc")
            pdp_list = db_pdps.get(soc_pdp, [])
            pdp_sel = st.selectbox("Plan de Prévention rattaché", pdp_list, key="pdp_sel")
            nom_pdp = st.text_input("Nom & Prénom de l'intervenant", key="pdp_nom")
        with col_p2:
            statut_pdp = st.selectbox("Statut de l'intervenant", ["N1 (Compagnon)", "N2 (Responsable)"], key="pdp_statut")
            if "N2" in statut_pdp:
                tel_pdp = st.text_input("N° Téléphone du Responsable N2", placeholder="06 XX XX XX XX", key="pdp_tel")
            else:
                tel_pdp = "Non requis (N1)"
            st.write("✍️ **Signature Tactile de l'Émargement :**")
            st.info(" [ Zone de Signature Tactile Empreinte / Stylet ] ")

        if st.button("✅ VALIDER L'ÉMARGEMENT DU PDP", type="primary"):
            if not nom_pdp:
                st.error("Veuillez renseigner le Nom & Prénom.")
            else:
                st.balloons()
                st.success(f"Émargement enregistré avec succès pour {nom_pdp} ({statut_pdp}) sur le {pdp_sel} !")
    else:
        st.subheader("🚀 Parcours Permis de Travail (WorkPermit / STA)")
        st.markdown("##### Étape 1 : Entreprise & Identification N2")
        c_rfid, c_soc = st.columns([1, 2])
        with c_rfid:
            st.info("💡 **Effet WOW Demonstration**")
            if st.button("💳 Simuler Passage Badge RFID / NFC", use_container_width=True):
                st.session_state.badge_active = True
                st.success("Badge Détecté : Léa DUSEK (ABYLSEN)")

        default_n2 = "Léa DUSEK" if st.session_state.get("badge_active") else "Léa DUSEK"
        with c_soc:
            soc_pt = st.selectbox("Entreprise Extérieure (EE)", list(db_pdps.keys()), index=0)
            pdp_pt = st.selectbox("Plan de Prévention (PDP)", db_pdps.get(soc_pt, []))
            mop_pt = st.selectbox("Mode Opératoire (MoP) rattaché", db_mops.get(pdp_pt, ["MoP Standard"]))
            n2_nom = st.selectbox("Responsable N2 présent", ["Léa DUSEK", "Matthieu MARTIN", "Alexandre LEFEBVRE"])
            mode_envoi = st.radio("Option d'envoi du permis :", ["Programmé (Validation Batch demain matin à 07h30)", "Immédiat (Chantier Urgence / Jour même)"], horizontal=True)

        st.divider()
        st.markdown("##### Étape 2 : Localisation & Mapping Sécurité Automatique")
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            zone_pt = st.selectbox("Zone du Chantier", list(db_zones.keys()))
            emplacement_pt = st.text_input("Précision d'emplacement (Texte libre)", value="1er étage, Bureau 104")
            map_data = db_zones.get(zone_pt, {})
            st.warning(f"""
            📍 **Mapping Sécurité Secteur Automatisé :**
            - **Point de Rassemblement (PR) :** `{map_data.get('pr')}`
            - **Zone de Confinement :** `{map_data.get('confinement')}`
            - **Poste d'Urgence :** `{map_data.get('urg')}`
            """)

        with col_loc2:
            st.markdown("##### Étape 3 : STA, EPIs & Dérogations")
            st.caption("⚠️ EPIs Obligatoires : Chaussures EN 20345, Casque + Jugulaire, Lunettes EN 166, Gilet, Gants Anti-coupure.")
            chk_effp2 = st.checkbox("Masque FFP2 / Protection Respiratoire")
            chk_harnais = st.checkbox("Harnais 2 Longes (Travail en Hauteur)")
            chk_bouchons = st.checkbox("Bouchons d'oreilles / Bruit > 80dB")
            st.write("**Permis Spécifiques (HRT) & Dérogations Déclenchées :**")
            chk_confine = st.checkbox("Espace Confiné (Mesures O2/H2S + Vigie obligatoire)")
            chk_loto = st.checkbox("Consignation / Déconsignation (LOTO)")
            chk_meuleuse = st.checkbox("Utilisation Meuleuse d'angle ➔ Dérogation Meuleuse")
            chk_casque_rouge = st.checkbox("Utilisation Cutter / Échelle ➔ Dérogation Casque Rouge")

        st.divider()
        st.markdown("##### Étape 4 : Co-signatures Tactiles de l'Équipe")
        col_comp1, col_comp2 = st.columns(2)
        with col_comp1:
            st.text_input("Compagnon 1 (Responsable N2)", value=f"{n2_nom} (N2)")
            st.caption("✍️ Signature reprise de l'émargement PDP")
        with col_comp2:
            st.text_input("Compagnon 2 (N1)", value="Matthieu MARTIN (N1)")
            st.caption("✍️ Signature tactile apposée sur borne")

        if st.button("🚀 SOUMETTRE LE PERMIS DE TRAVAIL", type="primary", use_container_width=True):
            derog_list = []
            if chk_meuleuse: derog_list.append("Meuleuse d'angle")
            if chk_casque_rouge: derog_list.append("Casque Rouge (Cutter/Échelle)")
            permis_list = []
            if chk_confine: permis_list.append("Espace Confiné")
            if chk_loto: permis_list.append("Consignation (LOTO)")

            nouveau_pt = {
                "id": f"PT-2026-0928-0{len(st.session_state.permis_db)+1}",
                "societe": soc_pt,
                "pdp": pdp_pt,
                "mop": mop_pt,
                "n2": n2_nom,
                "statut_n2": "N2 (Responsable)",
                "tel_n2": "06 12 34 56 78",
                "zone": zone_pt,
                "emplacement": emplacement_pt,
                "pr": map_data.get('pr'),
                "confinement": map_data.get('confinement'),
                "urg": map_data.get('urg'),
                "mode_envoi": "programmé" if "Programmé" in mode_envoi else "immédiat",
                "statut": "EN_ATTENTE_BATCH" if "Programmé" in mode_envoi else "VALIDÉ",
                "heure": datetime.datetime.now().strftime("%H:%M"),
                "produits": "Acétone / Solvant peinture",
                "epis": ["Chaussures EN 20345", "Casque + Jugulaire", "Lunettes EN 166", "Gilet Visibilité", "Gants Anti-coupure"],
                "permis_specifiques": permis_list,
                "derogations": derog_list,
                "compagnons": [f"{n2_nom} (N2)", "Matthieu MARTIN (N1)"]
            }
            st.session_state.permis_db.append(nouveau_pt)
            st.balloons()
            st.success(f"Permis {nouveau_pt['id']} créé avec succès ! Transmis au Donneur d'Ordre.")

elif role == "📊 Dashboard Live & Batch 07h30 (DO / HSE)":
    st.markdown("""
    <div class="pg-header" style='background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);'>
        <h2 style='margin:0;'>DDS BOARD & TABLEAU DE BORD DONNEUR D'ORDRE (DO)</h2>
        <p style='margin:0; opacity:0.8;'>Supervision Temps Réel des Activités & Validation Automatisée</p>
    </div>
    """, unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_permis = len(st.session_state.permis_db)
    en_attente = sum(1 for p in st.session_state.permis_db if p["statut"] == "EN_ATTENTE_BATCH")
    valides = sum(1 for p in st.session_state.permis_db if p["statut"] == "VALIDÉ")
    derogations = sum(1 for p in st.session_state.permis_db if len(p["derogations"]) > 0)

    kpi1.metric("Chantiers Totaux", total_permis)
    kpi2.metric("En Attente Batch (07h30)", en_attente)
    kpi3.metric("Permis Validés Actifs", valides)
    kpi4.metric("Dérogations Casque Rouge", derogations)
    st.divider()

    st.subheader("⚡ Validation Globale de la Fournée du Matin (Batch 07h30)")
    c_batch_txt, c_batch_btn = st.columns([3, 1])
    with c_batch_txt:
        st.write("Le script serveur traite la fournée quotidienne. En tant que Donneur d'Ordre, vous pouvez valider l'ensemble des permis de votre secteur en 1 seul clic.")
    with c_batch_btn:
        if st.button("✅ VALIDER LE BATCH (07h30)", type="primary", use_container_width=True):
            for p in st.session_state.permis_db:
                p["statut"] = "VALIDÉ"
            st.success("Fournée de 07h30 validée avec succès ! E-mails et QR Codes transmis aux N2.")

    st.subheader("📋 Liste des Permis du Jour")
    st.dataframe(st.session_state.permis_db, use_container_width=True)

else:
    st.markdown("""
    <div class="pg-header" style='background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);'>
        <h2 style='margin:0;'>AUDIT TERRAIN & SCAN QR CODE — CASQUE ROUGE</h2>
        <p style='margin:0; opacity:0.8;'>Contrôle de Conformité Instantané sur Zone de Chantier</p>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.subheader("📱 Smartphone Casque Rouge")
        pt_sel_scan = st.selectbox("Sélectionnez le permis à scanner sur chantier :", [p["id"] for p in st.session_state.permis_db])
        if st.button("🔍 Simuler Scan QR Code", type="primary", use_container_width=True):
            st.session_state.scanned = next(p for p in st.session_state.permis_db if p["id"] == pt_sel_scan)

    with col_s2:
        st.subheader("📄 Document Officiel A4 Numérisé")
        if "scanned" in st.session_state:
            p = st.session_state.scanned
            status_color = "#10b981" if p["statut"] == "VALIDÉ" else "#f59e0b"
            st.markdown(f"""
            <div style="background: white; border: 2px solid #003366; padding: 20px; border-radius: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="color:#003366; margin:0;">PERMIS DE TRAVAIL GÉNÉRAL (STA)</h3>
                    <span style="background:{status_color}; color:white; padding:4px 12px; border-radius:12px; font-weight:bold;">{p['statut']}</span>
                </div>
                <hr>
                <p><b>Réf :</b> {p['id']} | <b>Horodatage :</b> {p['heure']}</p>
                <p><b>Entreprise :</b> {p['societe']} | <b>PDP :</b> {p['pdp']}</p>
                <p><b>Mode Opératoire :</b> {p['mop']}</p>
                <p><b>Responsable N2 :</b> {p['n2']} ({p['tel_n2']})</p>
                <p><b>Emplacement :</b> {p['zone']} ({p['emplacement']})</p>
                <p><b>Point de Rassemblement :</b> {p['pr']} | <b>Confinement :</b> {p['confinement']}</p>
                <p><b>Permis Spécifiques / Dérogations :</b> {', '.join(p['permis_specifiques'] + p['derogations']) if (p['permis_specifiques'] or p['derogations']) else 'Aucun'}</p>
                <hr>
                <p style="text-align:center; color:#003366; font-weight:bold; margin:0;">
                    ✅ CO-SIGNATURES VECTORIELLES AUDITÉES & HORODATÉES EN BDD
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Cliquez sur 'Simuler Scan QR Code' pour afficher le permis numérisé A4.")
