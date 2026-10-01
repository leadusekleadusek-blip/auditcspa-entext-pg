import datetime
import json
import urllib.request
import Streamlit as st
import unicodedata
from fpdf import FPDF

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="P&G Amiens — e-Work Permit System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS P&G
st.markdown("""
<style>
    .stApp { background-color: #f8fafc !important; }
    .main { background-color: #f8fafc; }
    .pg-header {
        background: linear-gradient(135deg, #003366 0%, #0056b3 100%);
        color: white; padding: 22px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .welcome-card {
        background: white; border: 1px solid #cbd5e1; padding: 30px; border-radius: 12px;
        text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;
    }
    .weather-card {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border: 1px solid #0284c7; padding: 12px 18px; border-radius: 10px;
        margin-bottom: 20px; color: #0369a1;
    }
    .status-pending {
        background-color: #fef08a; color: #854d0e; border: 2px solid #eab308;
        padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.1rem;
        margin-bottom: 15px;
    }
    .status-validated {
        background-color: #dcfce7; color: #166534; border: 2px solid #22c55e;
        padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.1rem;
        margin-bottom: 15px;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    div[data-baseweb="input"] { background-color: #e0f2fe !important; border: 1.5px solid #0284c7 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] > div { background-color: #e0f2fe !important; border: 1.5px solid #0284c7 !important; border-radius: 8px !important; }
    .stepper-container { background: white; border: 1px solid #cbd5e1; border-radius: 12px; padding: 24px 20px 18px 20px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
    .stepper-wrapper { position: relative; display: flex; justify-content: space-between; align-items: flex-start; }
    .progress-track { position: absolute; top: 13px; left: 5%; right: 5%; height: 4px; background-color: #e2e8f0; z-index: 1; }
    .progress-fill { height: 100%; background-color: #10b981; transition: width 0.4s ease-in-out; }
    .step-item { display: flex; flex-direction: column; align-items: center; flex: 1; font-size: 0.8rem; font-weight: 600; color: #64748b; text-align: center; z-index: 2; }
    .step-badge { width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: bold; margin-bottom: 8px; background-color: white; border: 3px solid #cbd5e1; color: #64748b; transition: all 0.3s ease; }
    .step-completed .step-badge { background-color: #10b981; border-color: #10b981; color: white; }
    .step-completed { color: #059669; }
    .step-active .step-badge { background-color: #003366; border-color: #003366; color: white; box-shadow: 0 0 0 4px rgba(0, 51, 102, 0.2); }
    .step-active { color: #003366; font-weight: bold; }
    .step-upcoming .step-badge { background-color: white; border-color: #cbd5e1; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MÉTÉO EN DIRECT (OPEN-METEO API)
# ---------------------------------------------------------
@st.cache_data(ttl=1800)
def obtenir_meteo_amiens_live():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=49.8941&longitude=2.2957&daily=temperature_2m_max,temperature_2m_min,windgusts_10m_max,weathercode&timezone=Europe%2FParis"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            return {
                "temp_max_j0": round(data['daily']['temperature_2m_max'][0]),
                "temp_min_j0": round(data['daily']['temperature_2m_min'][0]),
                "vent_j0": round(data['daily']['windgusts_10m_max'][0]),
                "code_w_j0": data['daily']['weathercode'][0],
                "temp_max_j1": round(data['daily']['temperature_2m_max'][1]),
                "vent_j1": round(data['daily']['windgusts_10m_max'][1]),
                "source": "Open-Meteo Live API"
            }
    except Exception:
        return {"temp_max_j0": 18, "temp_min_j0": 8, "vent_j0": 14, "code_w_j0": 0, "temp_max_j1": 19, "vent_j1": 12, "source": "Mode Secours"}

# ---------------------------------------------------------
# RÉFÉRENTIELS & BDD P&G
# ---------------------------------------------------------
db_societes = ["ABYLSEN", "APAVE", "AXIMA", "ENGIE", "EULER", "SOUS-TRAITANCE-EXPERT"]

db_pdps = {
    "ABYLSEN": ["PDP-2026-042 (Bâtiment M1 - Rénovation)"],
    "APAVE": ["PDP-2026-104 (Inspection Pression Tuyauterie)"],
    "AXIMA": ["PDP-2026-015 (HVAC Zone Production M1)"],
    "ENGIE": ["PDP-2026-067 (Chaufferie Vapeur Nord)"],
    "EULER": ["PDP-2026-090 (Génie Civil & Terrassement TP)"],
    "SOUS-TRAITANCE-EXPERT": ["PDP-2026-042 (Sous-traitant rattaché à ABYLSEN)"]
}

db_mops = {
    "PDP-2026-042 (Bâtiment M1 - Rénovation)": [{"titre": "MoP-01: Peinture & Finitions", "st": False}],
    "PDP-2026-042 (Sous-traitant rattaché à ABYLSEN)": [{"titre": "MoP-02-ST: Électromécanique Spécialisée", "st": True, "titulaire": "ABYLSEN"}],
    "PDP-2026-104 (Inspection Pression Tuyauterie)": [{"titre": "MoP-01: Épreuve Hydraulique Tuyauterie", "st": False}],
    "PDP-2026-015 (HVAC Zone Production M1)": [{"titre": "MoP-01: Nettoyage Filtres CTA", "st": False}],
    "PDP-2026-067 (Chaufferie Vapeur Nord)": [{"titre": "MoP-01: Isoler Purgeur Vapeur", "st": False}],
    "PDP-2026-090 (Génie Civil & Terrassement TP)": [{"titre": "MoP-01: Fouille Terrassement TP", "st": False}]
}

db_n2 = ["Léa DUSEK", "Matthieu MARTIN", "Alexandre LEFEBVRE", "Cindy BERNARD"]

db_zones_carto = {
    "Bâtiment M1 - Zone Production": {"pr": "PR-2 (Parking Ouest)", "confinement": "ZC-01 (Hall M1)", "urgence": "03.22.54.33.33", "sprinkler": True, "detection": True},
    "Bâtiment M1 - Bureaux / Toiture": {"pr": "PR-2 (Parking Ouest)", "confinement": "ZC-01 (Hall M1)", "urgence": "03.22.54.30.00", "sprinkler": False, "detection": True},
    "Bâtiment M2 - Conditionnement": {"pr": "PR-4 (Zone Nord)", "confinement": "ZC-03 (Atrium M2)", "urgence": "03.22.54.33.34", "sprinkler": True, "detection": True},
    "Zone Extérieure / Logistique / TP": {"pr": "PR-1 (Entrée Principale)", "confinement": "ZC-00 (Poste Central)", "urgence": "03.22.54.33.33", "sprinkler": False, "detection": False}
}

db_materiaux = ["Acier / Carbone", "Inox 316L / 304L", "Aluminium", "Béton / Maçonnerie", "PVC / Plastique"]
db_disques_blanchiment = ["Disque fibre abrasif", "Brosse métallique torsadée", "Clean & Strip"]

etapes_noms = ["Date & EE", "PDP & MoP", "Responsable N2", "Zone & Urgences", "Check-list & EPIs", "Permis Spécifiques (HRT)", "Synthèse & Signatures"]

# BDD
if "permis_db" not in st.session_state:
    st.session_state.permis_db = []

if "kiosk_mode" not in st.session_state:
    st.session_state.kiosk_mode = "HOME"
if "step" not in st.session_state:
    st.session_state.step = 1

# Initialisation des données
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "date_str": datetime.date.today().strftime("%d/%m/%Y"),
        "societe": "ABYLSEN",
        "pdp": "PDP-2026-042 (Bâtiment M1 - Rénovation)",
        "mop": "MoP-01: Peinture & Finitions",
        "is_subcontractor": False,
        "titulaire_n2": "",
        "n2_nom": "Léa DUSEK",
        "lieu_pdp": "Bâtiment M1 - Bureaux / Toiture",
        "lieu_precision": "1er étage, Bureau 104",
        "description": "Maintenance et travaux sur site",
        "intervenants": ["Léa DUSEK", "Matthieu MARTIN"],
        
        # Triggers Permis Spécifiques
        "p_hauteur": False, "p_toiture": False, "p_points_chauds": False, "p_excavation": False,
        "p_grutage": False, "p_confine": False, "p_electrique": False, "p_consignation": False, "p_systeme_risque": False,

        # 1. HAUTEUR / NACELLE / ÉCHAFAUDAGE
        "h_pirl": False, "h_pirl_vgp": True, "h_pirl_soc": "ABYLSEN",
        "h_nacelle": False, "h_nacelle_vgp": True, "h_nacelle_caces": True, "h_nacelle_aut": True, "h_nacelle_harnais": True, "h_nacelle_soc": "ABYLSEN",
        "h_echaf": False, "h_echaf_type": "Utilisation",
        "h_echaf_montage_qualif": True, "h_echaf_montage_harnais": True,
        "h_echaf_util_qualif": True, "h_echaf_util_vgp": True, "h_echaf_util_certif": True, "h_echaf_util_verif_j": True, "h_echaf_soc": "ABYLSEN",

        # 2. ACCÈS TOITURE
        "toiture_protection": "Garde-corps périphériques conformes",
        "toiture_valideur": "Matthieu MARTIN (Habilité ePDP Accès Toiture)",

        # 3. POINT CHAUD
        "chaud_gants_type": "Gants de Soudeur Croûte de Cuir (EN 12477)",
        "chaud_extincteur1": "Eau + Additif 6L", "chaud_extincteur2": "CO2 5kg",
        "chaud_degage_10m": True, "chaud_baches": False,
        "chaud_traverse_mur": False, "chaud_vigie_opposee": False,
        "chaud_ouverture_10m": False, "chaud_obstruction": False,
        "chaud_vigie_nom": "Matthieu MARTIN",
        "chaud_heure_fin": "15:00", "chaud_heure_fin_ronde": "16:00",

        # 4. EXCAVATION / TRANCHÉE
        "excav_plans_eaux_indus": True, "excav_plans_eaux_usees": True, "excav_plans_eaux_pluv": True, "excav_plans_eaux_incendie": True,
        "excav_plans_ht": True, "excav_plans_bt": True, "excav_plans_gaz": True,
        "excav_struct_proximite": False, "excav_architecte": False, "excav_dict": True,
        "excav_pompe_eau": False, "excav_balisage": True, "excav_vehicule_3m": True, "excav_deblais": True,
        "excav_acces_type": "Escalier / Rampe sécurisée",
        "excav_profondeur_130": False, "excav_blindage": False,
        "excav_schema": "Fouille de 1.0m de profondeur pour raccordement.",
        "excav_chef_manoeuvre": "Léa DUSEK", "excav_do": "Matthieu MARTIN", "excav_casque_rouge": "Alexandre LEFEBVRE",

        # 5. GRUTAGE
        "grut_desc": "Levage groupe froid rooftop",
        "grut_poids_charge": 2500.0, "grut_poids_acc": 200.0, "grut_unite": "kg",
        "grut_immat": "GRUE-AMIENS-88", "grut_fleche": 35.0, "grut_portee": 20.0, "grut_pression_patin": "12 T/m²", "grut_rayon": 15.0,
        "grut_balisage": True, "grut_plan_vue": True, "grut_plan_elev": True, "grut_obstacles": True,
        "grut_anemometre": True, "grut_vent_mesure": 18.0, "grut_vent_unite": "km/h",
        "grut_dispo_pesage": True, "grut_centre_gravite": True, "grut_angles_elingue": True, "grut_plaques_rep": True,
        "grut_chef_m": "Léa DUSEK (ABYLSEN)", "grut_elingueur": "Matthieu MARTIN (ABYLSEN)", "grut_grutier": "Jean LEVAGE (APAVE)",
        "grut_certif_grue": True, "grut_certif_acc": True, "grut_certif_plaques": True, "grut_check_j_grue": True, "grut_check_j_acc": True,
        "grut_pattes_concu": True, "grut_pattes_defaut": False, "grut_pattes_adequation": True, "grut_charges_annexes": True,
        "grut_schema": "Schéma de levage sur stabilisateurs béton.",

        # 6. ESPACE CONFINÉ
        "conf_lieu": "Cuve C-102 Ligne 3",
        "conf_r_atmo": True, "conf_r_chimique": False, "conf_r_inflam": False, "conf_r_orga": False,
        "conf_r_meca": False, "conf_r_thermiq": False, "conf_r_bruit": False, "conf_troudhomme_610": True,
        "conf_catec": True, "conf_hauteur": False, "conf_m20": True,
        "conf_secouriste": "Attribué automatique (Poste M1)", "conf_medical": "Infirmerie Centrale M1",
        "conf_action_chaud": False, "conf_ventilation_nat": True, "conf_ventilation_forcee": True, "conf_ventilation_debit": "60 m3/h/pers",
        "conf_consignation_gaz": True, "conf_cuve_vide": True, "conf_vol_caches": False, "conf_eclairage_24v": True, "conf_blocage_ouvert": True,
        "conf_echaf_echelle": False, "conf_prod_chim": False, "conf_laser": False, "conf_comm_type": "Talkie-Walkie étanche",
        "conf_o2": 20.9, "conf_h2s_check": False, "conf_h2s": 0.0, "conf_co_check": False, "conf_co": 0.0, "conf_explo_check": False, "conf_explo": 0.0,
        "conf_temp_cuve": 22.0, "conf_verif_temp": "Léa DUSEK (N2)", "conf_inflam_lel": 0.0, "conf_verif_lel": "Léa DUSEK (N2)",
        "conf_entrant": "Léa DUSEK", "conf_standby": "Matthieu MARTIN", "conf_do": "Alexandre LEFEBVRE",

        # 7. TRAVAIL ÉLECTRIQUE
        "elec_modife": False, "elec_armoire": True, "elec_voisinage_tension": True, "elec_courant_faible": False,
        "elec_releve": True, "elec_chemins": False, "elec_voisinage_nues": False, "elec_valideur_ei": "Valideur E&I (Habilité B2V/HC)",

        # 8. CONSIGNATION LOTO (3 PHASES)
        "loto_methode_ouverture": "2 vannes et vanne de drain", "loto_loc1": "Vanne V-101 Amont", "loto_loc2": "Vanne V-102 Aval / Drain D-01",
        "loto_is_elec": True, "loto_is_elec_loc1": "TGBT-M1-Armoire 4", "loto_is_elec_loc2": "Cadenas LOTO #884",
        "loto_is_pneu": False, "loto_is_hydra": False, "loto_is_residu": True, "loto_is_residu_loc1": "Purge pression résiduelle", "loto_is_residu_loc2": "Manomètre à 0 bar",
        "loto_drain_ouvert": True, "loto_eq_ouvert": True, "loto_eq_lave": True, "loto_eq_sanitise": True,

        # 9. SYSTÈME À RISQUES / ATEX / CHIMIQUE
        "sr_chimique_c1": False, "sr_chimique_nom": "", "sr_fluide_dang": False, "sr_fluide_nom": "", "sr_atex": False, "sr_atex_nom": "",
        "sr_balisage": True, "sr_douche_rince": True, "sr_ramonage": False, "sr_ramonage_dt": "01/10/2026 08:00",
        "sr_isolement": True, "sr_feuille_loto": True, "sr_zonage_atex": True,
        "sr_epi_ecran": True, "sr_epi_lunettes": False, "sr_epi_gants_chim": True, "sr_epi_comb1": False, "sr_epi_comb2": True,
        "sr_epi_bottes": True, "sr_epi_cartouche": True, "sr_epi_ari": False, "sr_epi_3m6000": False, "sr_epi_versaflo": False,
        "sr_auxiliaire_equipe": True, "sr_comm_moyen": "Talkie-Walkie ATEX",
        "sr_inspect_remise": True, "sr_inspect_nom": "Léa DUSEK", "sr_inspect_dt": "01/10/2026 17:00",
        "sr_sign_intervenant": "Léa DUSEK", "sr_sign_do": "Matthieu MARTIN", "sr_sign_operations": "Alexandre LEFEBVRE",

        # STA & Outillage
        "sta_prod_chimique": False, "produits_liste": "", "sta_dta": False,
        "sta_electroportatif": False, "sta_meuleuse": False,
        "meuleuse_diametre": "125 mm", "meuleuse_operateurs": ["Léa DUSEK"], "meuleuse_marque": "Bosch Pro", "meuleuse_alim": "Batterie 18V", "meuleuse_ref": "MEU-042", "meuleuse_vitesse": "11000",
        "meu_env_plain_pied": True, "meu_env_hauteur": False, "meu_env_confine": False, "meu_env_excavation": False, "meu_env_stable": True, "meu_env_maintien_2mains": True, "meu_env_piece_fixee": True, "meu_env_hors_ligne_tir": True, "meu_position_op": "Debout",
        "meuleuse_u_decoupe": False, "meuleuse_mat_decoupe": db_materiaux[0], "meuleuse_u_ebavurage": False, "meuleuse_mat_ebavurage": db_materiaux[0], "meuleuse_u_flap": False, "meuleuse_u_blanchiment": False, "meuleuse_disque_blanchiment": db_disques_blanchiment[0],
        "sta_pirl_nacelle": False, "sta_couteau_lame": False, "sta_echelle_escabeau": False,

        # Dangers & EPIs
        "r_exigu": False, "r_superpose": False, "r_inconfortable": False, "r_fumee_poussiere": False, "r_bruit_80db": False, "r_eq_mouvement": False, "r_chute_objets": False, "r_vehicule": False, "r_escalier": False, "r_bords_tranchants": False, "r_metaux_chaud": False, "r_feu_flamme": False, "r_cables_sol": False,
        "epi_lunettes_chantier_visiere": True, "epi_lunettes_etanches": False, "epi_visiere_idra": False, "epi_pare_visage": False, "epi_casque_jugulaire": False, "epi_casque_auditif": False, "epi_gants_coupure": True, "epi_gants_manutention": False, "epi_gants_chimique": False, "epi_gants_electrique": False, "epi_bouchons_jetables": False, "epi_bouchons_moules": False, "epi_ffp1_ffp2": False, "epi_3m6000": False, "epi_versaflo": False, "epi_cartouche_abek": False, "epi_autre": ""
    }

# ---------------------------------------------------------
# NETTOYAGE DES TEXTES POUR POLICES FPDF
# ---------------------------------------------------------
def sanitize_text(text):
    if not isinstance(text, str): text = str(text)
    text = text.replace("🔥", "[Pt Chaud]").replace("🦺", "[Confiné]").replace("🧗", "[Hauteur]").replace("⚡", "[LOTO]").replace("⚠️", "[!]").replace("✅", "[OK]").replace("🚜", "[Excavation]")
    normalized = unicodedata.normalize('NFKD', text)
    cleaned = ''.join(c for c in normalized if not unicodedata.combining(c))
    return cleaned.encode('latin-1', 'ignore').decode('latin-1')

# ---------------------------------------------------------
# GENERATION PDF
# ---------------------------------------------------------
def generer_pdf_bytes(permis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_fill_color(0, 51, 102)
    pdf.rect(10, 10, 190, 22, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.text(15, 20, sanitize_text("PROCTER & GAMBLE AMIENS - e-Work Permit System"))
    pdf.set_font("Helvetica", "", 10)
    pdf.text(15, 27, sanitize_text(f"Ref: {permis['id']} | Date: {permis['date_travaux']} | Heure: {permis['heure']}"))
    pdf.set_y(38)

    if permis['statut'] == 'VALIDÉ':
        pdf.set_fill_color(220, 252, 231); pdf.set_draw_color(34, 197, 94); pdf.set_text_color(22, 101, 52)
        status_str = "PERMIS VALIDE PAR LE DONNEUR D'ORDRE"
    else:
        pdf.set_fill_color(254, 240, 138); pdf.set_draw_color(234, 179, 8); pdf.set_text_color(133, 77, 14)
        status_str = "PERMIS EN ATTENTE DE VALIDATION BATCH (07h30)"

    pdf.rect(10, 38, 190, 10, 'DF')
    pdf.set_font("Helvetica", "B", 11)
    pdf.text(15, 44.5, sanitize_text(status_str))
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(54)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, sanitize_text("1. INFORMATIONS GENERALES & SOUS-TRAITANCE"), 0, 1)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, sanitize_text(f"Societe Intervenante: {permis['societe']} | PDP: {permis['pdp']}"), 0, 1)
    if permis.get("is_subcontractor"):
        pdf.cell(0, 5, sanitize_text(f"[SOUS-TRAITANCE DETECTEE] N2 Titulaire Obligatoire: {permis.get('titulaire_n2')}"), 0, 1)
    pdf.cell(0, 5, sanitize_text(f"Responsable N2 Site: {permis['n2']} | Secteur: {permis['zone']} ({permis.get('emplacement', '')})"), 0, 1)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, sanitize_text("2. SYNTHESE DES RISQUES ET MOYENS DE PREVENTION"), 0, 1)
    pdf.set_font("Helvetica", "B", 8); pdf.set_fill_color(241, 245, 249)
    pdf.cell(60, 6, sanitize_text("Activite Cochee"), 1, 0, 'L', True)
    pdf.cell(65, 6, sanitize_text("Risque Identifie"), 1, 0, 'L', True)
    pdf.cell(65, 6, sanitize_text("Moyens de Prevention / EPIs"), 1, 1, 'L', True)

    pdf.set_font("Helvetica", "", 8)
    for r in permis.get("tableau_risques", []):
        pdf.cell(60, 6, sanitize_text(str(r.get("activite", "")))[:32], 1, 0)
        pdf.cell(65, 6, sanitize_text(str(r.get("risque", "")))[:36], 1, 0)
        pdf.cell(65, 6, sanitize_text(str(r.get("prevention", "")))[:36], 1, 1)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, sanitize_text("3. PERMIS SPECIFIQUES ET DEROGATIONS"), 0, 1)
    pdf.set_font("Helvetica", "", 9)
    spe_all = permis.get('permis_specifiques', []) + permis.get('derogations', [])
    pdf.cell(0, 5, sanitize_text(" - " + (", ".join(spe_all) if spe_all else "Aucun permis specifique requis")), 0, 1)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, sanitize_text("4. SIGNATURES AUDITEES"), 0, 1)
    pdf.set_font("Helvetica", "", 8)
    for sign in permis.get("intervenants", []):
        pdf.cell(0, 5, sanitize_text(f" [OK] Signature horodatee sur borne tactile : {sign}"), 1, 1)

    return bytes(pdf.output())

# ---------------------------------------------------------
# BARRE LATÉRALE
# ---------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Procter_%26_Gamble_logo.svg/1024px-Procter_%26_Gamble_logo.svg.png", width=80)
st.sidebar.title("e-Work Permit P&G")
st.sidebar.caption("Site d'Amiens — Solution Unifiée")

role = st.sidebar.radio(
    "Interface à démontrer :",
    ["🖥️ Borne Kiosk Tactile (EE / N2)", "📊 DDS Board & Batch 07h30 (DO / HSE)", "📱 Inspection Terrain QR Code (Casque Rouge)"]
)

# ==============================================================================
# INTERFACE 1 : BORNE KIOSK TACTILE (EE / N2)
# ==============================================================================
if role == "🖥️ Borne Kiosk Tactile (EE / N2)":

    st.markdown("""
    <div class="pg-header">
        <h1 style='margin:0; font-size: 2.1rem;'>PROCTER & GAMBLE — AMIENS</h1>
        <p style='margin:4px 0 0 0; opacity:0.85; font-size: 1.05rem;'>WORK PERMIT IT | BORNE TACTILE KIOSK</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.kiosk_mode == "HOME":
        st.write("### Veuillez sélectionner votre démarche :")
        st.write("")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            st.markdown("<div class='welcome-card'><h2 style='color:#003366;'>🚀 Permis de Travail</h2><p>Émettre un nouveau Permis de Travail (STA, Check-list, EPIs normés & Signatures).</p></div>", unsafe_allow_html=True)
            if st.button("🚀 COMMENCER UN PERMIS DE TRAVAIL", type="primary", use_container_width=True):
                st.session_state.kiosk_mode = "PERMIS"; st.session_state.step = 1; st.rerun()
        with col_act2:
            st.markdown("<div class='welcome-card'><h2 style='color:#003366;'>📝 Émargement PDP</h2><p>Émarger et signer un Plan de Prévention enregistré pour votre entreprise.</p></div>", unsafe_allow_html=True)
            if st.button("📝 SIGNER UN PLAN DE PRÉVENTION (PDP)", use_container_width=True):
                st.session_state.kiosk_mode = "PDP"; st.rerun()

    elif st.session_state.kiosk_mode == "PDP":
        if st.button("⬅️ Retour à l'accueil"): st.session_state.kiosk_mode = "HOME"; st.rerun()
        st.subheader("📝 Émargement d'un Plan de Prévention (PDP)")
        st.divider()
        soc_pdp = st.selectbox("1. Sélectionnez votre Entreprise Extérieure (EE) :", db_societes)
        pdp_sel = st.selectbox(f"2. Plans de Prévention enregistrés pour {soc_pdp} :", db_pdps.get(soc_pdp, ["Aucun PDP"]))
        nom_pdp = st.text_input("Nom & Prénom de l'intervenant :")
        statut_pdp = st.selectbox("Statut sur le chantier :", ["N1 (Compagnon)", "N2 (Responsable)"])
        st.info(" [ Zone de Signature Tactile Empreinte / Stylet ] ")
        if st.button("✅ VALIDER L'ÉMARGEMENT DU PDP", type="primary", use_container_width=True):
            st.balloons(); st.success(f"Émargement validé pour {nom_pdp} !"); st.session_state.kiosk_mode = "HOME"

    elif st.session_state.kiosk_mode == "PERMIS":
        current_step = st.session_state.step
        total_steps = len(etapes_noms)
        progress_pct = int(((current_step - 1) / (total_steps - 1)) * 100)

        steps_items_html = ""
        for idx, name in enumerate(etapes_noms, 1):
            if idx < current_step: steps_items_html += f'<div class="step-item step-completed"><div class="step-badge">✓</div><span>{name}</span></div>'
            elif idx == current_step: steps_items_html += f'<div class="step-item step-active"><div class="step-badge">{idx}</div><span>{name}</span></div>'
            else: steps_items_html += f'<div class="step-item step-upcoming"><div class="step-badge">{idx}</div><span>{name}</span></div>'

        st.markdown(f'<div class="stepper-container"><div class="stepper-wrapper"><div class="progress-track"><div class="progress-fill" style="width: {progress_pct}%;"></div></div>{steps_items_html}</div></div>', unsafe_allow_html=True)

        if current_step == 1:
            st.subheader("1. Date d'Intervention & Entreprise Extérieure")
            c1, c2 = st.columns(2)
            today_date = datetime.date.today(); tomorrow_date = today_date + datetime.timedelta(days=1)
            with c1:
                date_choice = st.radio("Date de planification du permis :", [f"Aujourd'hui : {today_date.strftime('%d/%m/%Y')}", f"Pour demain : {tomorrow_date.strftime('%d/%m/%Y')}"])
                st.session_state.form_data["date_str"] = tomorrow_date.strftime("%d/%m/%Y") if "demain" in date_choice else today_date.strftime("%d/%m/%Y")
            with c2:
                st.session_state.form_data["societe"] = st.selectbox("Entreprise Extérieure (EE) :", db_societes)

            c_back, c_next = st.columns(2)
            with c_back:
                if st.button("⬅️ Accueil"): st.session_state.kiosk_mode = "HOME"; st.rerun()
            with c_next:
                if st.button("Suivant ➔", type="primary"): st.session_state.step = 2; st.rerun()

        elif current_step == 2:
            st.subheader(f"2. Plan de Prévention, Mode Opératoire & Règle de Sous-Traitance")
            p_list = db_pdps.get(st.session_state.form_data["societe"], ["PDP Standard"])
            st.session_state.form_data["pdp"] = st.selectbox("Plan de Prévention (PDP) rattaché :", p_list)
            
            m_obj_list = db_mops.get(st.session_state.form_data["pdp"], [{"titre": "MoP Standard", "st": False}])
            m_titles = [m["titre"] for m in m_obj_list]
            selected_mop_title = st.selectbox("Mode Opératoire (MoP) :", m_titles)
            st.session_state.form_data["mop"] = selected_mop_title
            
            mop_info = next((m for m in m_obj_list if m["titre"] == selected_mop_title), {"st": False})
            st.session_state.form_data["is_subcontractor"] = mop_info.get("st", False)

            if st.session_state.form_data["is_subcontractor"]:
                st.warning(f"⚠️ **Sous-traitance Détectée :** Ce Mode Opératoire identifie une intervention en sous-traitance pour la société **{mop_info.get('titulaire', 'ABYLSEN')}**.")
                st.session_state.form_data["titulaire_n2"] = st.text_input("Nom & Prénom du Responsable N2 de la Société Titulaire du PDP :", value=mop_info.get('titulaire', 'ABYLSEN') + " - Représentant N2")
            else:
                st.success("✅ Intervention directe par la société titulaire du PDP.")

            c_back, c_next = st.columns(2)
            with c_back:
                if st.button("⬅️ Précédent"): st.session_state.step = 1; st.rerun()
            with c_next:
                if st.button("Suivant ➔", type="primary"): st.session_state.step = 3; st.rerun()

        elif current_step == 3:
            st.subheader("3. Responsable N2 Présent sur le Chantier")
            st.session_state.form_data["n2_nom"] = st.selectbox("Responsable N2 qualifié sur site :", db_n2)
            c_back, c_next = st.columns(2)
            with c_back:
                if st.button("⬅️ Précédent"): st.session_state.step = 2; st.rerun()
            with c_next:
                if st.button("Suivant ➔", type="primary"): st.session_state.step = 4; st.rerun()

        elif current_step == 4:
            st.subheader("4. Localisation & Assignation Automatique des Urgences")
            st.session_state.form_data["lieu_pdp"] = st.selectbox("Zone du Chantier :", list(db_zones_carto.keys()))
            st.session_state.form_data["lieu_precision"] = st.text_input("Précision d'emplacement (Local, Bureau, Ligne) :", value=st.session_state.form_data["lieu_precision"])
            st.session_state.form_data["description"] = st.text_input("Description détaillée de la tâche :", value=st.session_state.form_data["description"])

            carto = db_zones_carto.get(st.session_state.form_data["lieu_pdp"], {})
            st.warning(f"📍 **Secours Secteur :** PR: `{carto.get('pr')}` | Confinement: `{carto.get('confinement')}` | Urgence: `{carto.get('urgence')}`")

            c_back, c_next = st.columns(2)
            with c_back:
                if st.button("⬅️ Précédent"): st.session_state.step = 3; st.rerun()
            with c_next:
                if st.button("Suivant ➔", type="primary"): st.session_state.step = 5; st.rerun()

        elif current_step == 5:
            st.subheader("5. Check-list, Déclencheurs HRT & EPIs Normés P&G")

            meteo_live = obtenir_meteo_amiens_live()
            is_demain = st.session_state.form_data["date_str"] != datetime.date.today().strftime("%d/%m/%Y")
            vitesse_vent = meteo_live["vent_j1"] if is_demain else meteo_live["vent_j0"]
            temp_j = meteo_live["temp_max_j0"]

            st.markdown(f"<div class='weather-card'>🌤️ <b>Météo Amiens :</b> {temp_j}°C | Vent : <b>{vitesse_vent} km/h</b> <i>({meteo_live['source']})</i></div>", unsafe_allow_html=True)

            st.error("🚨 **Cochez les activités pour ouvrir les Permis Spécifiques (Étape 6) :**")
            c_rp1, c_rp2 = st.columns(2)
            with c_rp1:
                st.session_state.form_data["p_hauteur"] = st.checkbox("Travail en hauteur / Échafaudage / Nacelle ➔ Permis Hauteur", value=st.session_state.form_data["p_hauteur"])
                st.session_state.form_data["p_toiture"] = st.checkbox("Accès toiture ➔ Permis Accès Toiture", value=st.session_state.form_data["p_toiture"])
                
                if st.session_state.form_data.get("sta_meuleuse"):
                    st.session_state.form_data["p_points_chauds"] = True
                
                st.session_state.form_data["p_points_chauds"] = st.checkbox("Génération de points chauds / flamme ➔ Permis Point Chaud", value=st.session_state.form_data["p_points_chauds"])
                st.session_state.form_data["p_excavation"] = st.checkbox("Tranchée, BTP, Ouverture de sol ➔ Permis Excavation", value=st.session_state.form_data["p_excavation"])
                st.session_state.form_data["p_grutage"] = st.checkbox("Grutage & Levage ➔ Permis Grutage", value=st.session_state.form_data["p_grutage"])

            with c_rp2:
                st.session_state.form_data["p_confine"] = st.checkbox("Espace confiné / Risque d'asphyxie ➔ Permis Espace Confiné", value=st.session_state.form_data["p_confine"])
                st.session_state.form_data["p_electrique"] = st.checkbox("Travail électrique / Voisinage ➔ Permis Travail Électrique", value=st.session_state.form_data["p_electrique"])
                
                loto_trigger = st.checkbox("Ouverture circuit sous pression / Machines en mouvement / Équipement sous pression / Laser IV ➔ Permis Consignation (LOTO)", value=st.session_state.form_data["p_consignation"])
                st.session_state.form_data["p_consignation"] = loto_trigger
                
                sr_trigger = st.checkbox("Risque chimique particulier / Zone ATEX / Fluides dangereux ➔ Permis Systèmes à Risques", value=st.session_state.form_data["p_systeme_risque"])
                st.session_state.form_data["p_systeme_risque"] = sr_trigger
                if sr_trigger: st.session_state.form_data["p_consignation"] = True

            st.divider()

            # Verrouillages EPIs Automatiques
            if st.session_state.form_data["p_hauteur"] or st.session_state.form_data["p_toiture"]:
                st.session_state.form_data["epi_casque_jugulaire"] = True
            if st.session_state.form_data["p_electrique"]:
                st.session_state.form_data["epi_gants_electrique"] = True
            if st.session_state.form_data["p_points_chauds"]:
                st.session_state.form_data["epi_visiere_idra"] = True; st.session_state.form_data["epi_gants_coupure"] = True

            st.write("##### 🥽 Équipements de Protection Individuelle (EPIs Normés P&G)")
            ce1, ce2, ce3, ce4 = st.columns(4)
            with ce1:
                st.session_state.form_data["epi_lunettes_chantier_visiere"] = st.checkbox("Lunettes EN 166", value=st.session_state.form_data["epi_lunettes_chantier_visiere"])
                st.session_state.form_data["epi_visiere_idra"] = st.checkbox("Écran facial EN 166B", value=st.session_state.form_data["epi_visiere_idra"])
            with ce2:
                st.session_state.form_data["epi_casque_jugulaire"] = st.checkbox("Casque Jugulaire EN 397", value=st.session_state.form_data["epi_casque_jugulaire"])
                st.session_state.form_data["epi_bouchons_moules"] = st.checkbox("Bouchons moulés", value=st.session_state.form_data["epi_bouchons_moules"])
            with ce3:
                st.session_state.form_data["epi_gants_coupure"] = st.checkbox("Gants anti-coupure 4543", value=st.session_state.form_data["epi_gants_coupure"])
                st.session_state.form_data["epi_gants_electrique"] = st.checkbox("Gants électriques EN 60903", value=st.session_state.form_data["epi_gants_electrique"])
            with ce4:
                st.session_state.form_data["epi_cartouche_abek"] = st.checkbox("Masque Cartouche ABEK", value=st.session_state.form_data["epi_cartouche_abek"])

            c_back, c_next = st.columns(2)
            with c_back:
                if st.button("⬅️ Précédent"): st.session_state.step = 4; st.rerun()
            with c_next:
                if st.button("Suivant ➔", type="primary"): st.session_state.step = 6; st.rerun()

        # =====================================================
        # ÉTAPE 6 : FORMULAIRES DÉTAILLÉS SELON L'ARBORESCENCE LOGIQUE
        # =====================================================
        elif current_step == 6:
            st.subheader("6. Formulaires Spécifiques (HRT) & Règles Métier")
            has_spe = False

            # --- 1. TRAVAIL EN HAUTEUR / NACELLE / ÉCHAFAUDAGE ---
            if st.session_state.form_data["p_hauteur"]:
                has_spe = True
                st.error("🧗 **PERMIS TRAVAIL EN HAUTEUR / ÉCHAFAUDAGE / NACELLE**")
                st.info("🔒 **EPI Obligatoire :** Casque avec jugulaire (EN 397) verrouillé automatiquement.")

                ch1, ch2, ch3 = st.columns(3)
                with ch1:
                    st.session_state.form_data["h_pirl"] = st.checkbox("PIRL (Gazelle)", value=st.session_state.form_data["h_pirl"])
                    if st.session_state.form_data["h_pirl"]:
                        st.session_state.form_data["h_pirl_vgp"] = st.checkbox("VGP + Contrôle visuel avant utilisation", value=True)
                        st.session_state.form_data["h_pirl_soc"] = st.text_input("Société propriétaire PIRL :", value=st.session_state.form_data["societe"])
                
                with ch2:
                    st.session_state.form_data["h_nacelle"] = st.checkbox("Nacelle (PEMP)", value=st.session_state.form_data["h_nacelle"])
                    if st.session_state.form_data["h_nacelle"]:
                        st.session_state.form_data["h_nacelle_vgp"] = st.checkbox("VGP + Check-list journalière", value=True)
                        st.session_state.form_data["h_nacelle_caces"] = st.checkbox("CACES R486 (Utilisateur & Vigie sol)", value=True)
                        st.session_state.form_data["h_nacelle_aut"] = st.checkbox("Autorisation de conduite employeur", value=True)
                        st.session_state.form_data["h_nacelle_harnais"] = st.checkbox("Qualification Hauteur (Port du Harnais)", value=True)
                        st.warning("🦺 **EPI Nacelle requis :** Harnais anti-chute + Longe courte d'assujettissement.")

                with ch3:
                    st.session_state.form_data["h_echaf"] = st.checkbox("Échafaudage", value=st.session_state.form_data["h_echaf"])
                    if st.session_state.form_data["h_echaf"]:
                        st.session_state.form_data["h_echaf_type"] = st.radio("Type d'intervention Échafaudage :", ["Montage / Démontage / Modification", "Utilisation simple"])
                        if "Montage" in st.session_state.form_data["h_echaf_type"]:
                            st.session_state.form_data["h_echaf_montage_qualif"] = st.checkbox("Qualification spécifique Montage Échafaudage", value=True)
                            st.error("🦺 **EPIs Montage :** Harnais + Double longe + Connecteurs MGO + Absorbeur + Gants.")
                        else:
                            st.session_state.form_data["h_echaf_util_qualif"] = st.checkbox("Qualification utilisation & inspection", value=True)
                            st.session_state.form_data["h_echaf_util_certif"] = st.checkbox("Certificat de montage affiché (Panneau Vert)", value=True)
                            st.session_state.form_data["h_echaf_util_verif_j"] = st.checkbox("Vérification journalière par société utilisatrice", value=True)
                st.divider()

            # --- 2. ACCÈS TOITURE ---
            if st.session_state.form_data["p_toiture"]:
                has_spe = True
                st.error("🏢 **PERMIS ACCÈS TOITURE**")
                st.info(f"📍 **Localisation Toiture :** `{st.session_state.form_data['lieu_pdp']}` ({st.session_state.form_data['lieu_precision']})")
                
                meteo_live = obtenir_meteo_amiens_live()
                vent_actuel = meteo_live["vent_j0"]
                temp_actuelle = meteo_live["temp_max_j0"]
                
                # Contrôle strict Météo Toiture
                refus_meteo = False
                motif_refus = ""
                
                if temp_actuelle < 3 or temp_actuelle > 30:
                    refus_meteo = True; motif_refus = f"Température extrême ({temp_actuelle}°C, hors plage 3°C - 30°C)"
                elif vent_actuel > 36:
                    refus_meteo = True; motif_refus = f"Rafales de vent supérieures au seuil ({vent_actuel} km/h > 36 km/h)"
                
                if refus_meteo:
                    st.error(f"❌ **ACCÈS TOITURE REFUSÉ PAR LE SYSTÈME :** {motif_refus}")
                else:
                    st.success(f"✅ **Conditions Météo Favorables :** Température {temp_actuelle}°C | Vent {vent_actuel} km/h (< 30 km/h)")
                    st.warning("⚠️ **Rappel Réglementaire P&G :** Accès à DEUX personnes impérativement. Un intervenant ne doit JAMAIS rester seul sur la toiture.")
                    
                    st.session_state.form_data["toiture_protection"] = st.selectbox(
                        "Identifier les moyens de protection de la zone :",
                        ["Garde-corps permanents périphériques (Protection Passive)", "Zone à moins de 3m du bord (Harnais + Longe d'arrêt de chute obligatoire)", "Ligne de vie conforme EN 795"]
                    )
                    st.session_state.form_data["toiture_valideur"] = st.text_input("Personne habilitée ePDP à valider l'accès toiture :", value=st.session_state.form_data["toiture_valideur"])
                st.divider()

            # --- 3. PERMIS POINT CHAUD ---
            if st.session_state.form_data["p_points_chauds"]:
                has_spe = True
                st.warning("🔥 **PERMIS POINT CHAUD / FLAMME / MEULAGE**")
                
                carto = db_zones_carto.get(st.session_state.form_data["lieu_pdp"], {})
                st.info(f"<b>Détection automatique des moyens d'extinction de la zone :</b> Sprinklers: `{carto.get('sprinkler')}` | Détection Fumée: `{carto.get('detection')}`", unsafe_allow_html=True)
                
                if not carto.get('sprinkler') or not carto.get('detection'):
                    st.error("🚨 **Surveillance P&G de 60 minutes SUPPLÉMENTAIRE obligatoire** après les 60 min de surveillance de l'Entreprise Extérieure (Zone sans sprinkler/détection automatique).")

                st.session_state.form_data["chaud_gants_type"] = st.selectbox("Sélection des gants Point Chaud obligatoires :", ["Gants de Soudeur Croûte de Cuir (EN 12477)", "Gants résistant à la chaleur de contact", "Gants anti-coupure 4543 pour meulage"])
                
                c_ext1, c_ext2 = st.columns(2)
                with c_ext1: st.session_state.form_data["chaud_extincteur1"] = st.selectbox("Extincteur 1 sur zone :", ["Eau + Additif 6L", "Poudre ABC 6kg", "CO2 5kg"])
                with c_ext2: st.session_state.form_data["chaud_extincteur2"] = st.selectbox("Extincteur 2 sur zone :", ["CO2 5kg", "Eau + Additif 6L", "Poudre ABC 6kg"])

                st.session_state.form_data["chaud_degage_10m"] = st.checkbox("Zone dégagée de tout combustible sur un rayon de 10m", value=st.session_state.form_data["chaud_degage_10m"])
                if not st.session_state.form_data["chaud_degage_10m"]:
                    st.error("🔒 **Protection requise :** Installation obligatoire de bâches/couvertures ignifugées M0 sur les matériaux restants.")

                st.session_state.form_data["chaud_traverse_mur"] = st.checkbox("Les travaux traversent une paroi ou un mur", value=st.session_state.form_data["chaud_traverse_mur"])
                if st.session_state.form_data["chaud_traverse_mur"]:
                    st.error("🔒 **Vigie secondaire obligatoire de l'autre côté du mur.**")

                st.session_state.form_data["chaud_vigie_nom"] = st.selectbox("Désignation de la Vigie du Point Chaud (signataire du MoP) :", st.session_state.form_data["intervenants"])
                
                c_h1, c_h2 = st.columns(2)
                with c_h1: st.session_state.form_data["chaud_heure_fin"] = st.text_input("Heure de fin des travaux à chaud :", value="15:00")
                with c_h2: st.session_state.form_data["chaud_heure_fin_ronde"] = st.text_input("Heure de fin de la ronde de surveillance (1h minimum post-chauffe) :", value="16:00")
                st.divider()

            # --- 4. EXCAVATION / TRANCHÉE ---
            if st.session_state.form_data["p_excavation"]:
                has_spe = True
                st.warning("🚜 **PERMIS EXCAVATION / TRANCHÉE / OUVERTURE DE SOL**")
                
                st.markdown("##### 1. Risques liés aux réseaux souterrains (Connaissance des plans)")
                ce_r1, ce_r2, ce_r3, ce_r4 = st.columns(4)
                with ce_r1:
                    st.session_state.form_data["excav_plans_eaux_indus"] = st.checkbox("Eaux Indu. / Potable", value=True)
                    st.session_state.form_data["excav_plans_eaux_usees"] = st.checkbox("Eaux Usées", value=True)
                with ce_r2:
                    st.session_state.form_data["excav_plans_eaux_pluv"] = st.checkbox("Eaux Pluviales", value=True)
                    st.session_state.form_data["excav_plans_eaux_incendie"] = st.checkbox("Eaux Incendie", value=True)
                with ce_r3:
                    st.session_state.form_data["excav_plans_ht"] = st.checkbox("Haute Tension", value=True)
                    st.session_state.form_data["excav_plans_bt"] = st.checkbox("Basse Tension", value=True)
                with ce_r4:
                    st.session_state.form_data["excav_plans_gaz"] = st.checkbox("Gaz Naturel", value=True)
                    st.session_state.form_data["excav_dict"] = st.checkbox("DICT émise et validée", value=True)

                st.markdown("##### 2. Prévention des Effondrements & Accès")
                st.session_state.form_data["excav_acces_type"] = st.selectbox("Moyens d'accès à la tranchée :", ["Escalier / Rampe amagée", "Échelle (Déclencher Dérogation Casque Rouge)", "Passerelle avec garde-corps"])
                if "Échelle" in st.session_state.form_data["excav_acces_type"]:
                    st.warning("⚠️ **Dérogation Casque Rouge activée :** Utilisation d'une échelle d'accès en excavation.")

                st.session_state.form_data["excav_profondeur_130"] = st.checkbox("Profondeur de la tranchée > 1,30 m", value=st.session_state.form_data["excav_profondeur_130"])
                if st.session_state.form_data["excav_profondeur_130"]:
                    st.error("🔒 **BLINDAGE OU TALUTAGE STRICTEMENT OBLIGATOIRE (Profondeur > 1,30m).**")

                st.info("✍️ **3 Signatures Obligatoires :** Chef de Manœuvre EE + Donneur d'Ordre P&G + Casque Rouge (Obligatoire avant démarrage).")
                st.divider()

            # --- 5. PERMIS GRUTAGE & LEVAGE ---
            if st.session_state.form_data["p_grutage"]:
                has_spe = True
                st.info("🏗️ **PERMIS GRUTAGE & OPÉRATIONS DE LEVAGE**")
                
                cg1, cg2, cg3 = st.columns(3)
                with cg1: st.session_state.form_data["grut_poids_charge"] = st.number_input("Poids de la charge :", value=2500.0)
                with cg2: st.session_state.form_data["grut_poids_acc"] = st.number_input("Poids des accessoires (élingues/manilles) :", value=200.0)
                with cg3: st.session_state.form_data["grut_unite"] = st.selectbox("Unité de poids :", ["kg", "Tonnes"])

                poids_tot = st.session_state.form_data["grut_poids_charge"] + st.session_state.form_data["grut_poids_acc"]
                st.write(f"⚖️ **Poids Total Calculé à gruter :** `{poids_tot} {st.session_state.form_data['grut_unite']}`")

                st.session_state.form_data["grut_dispo_pesage"] = st.checkbox("Dispositif de mesure de charge sur grue", value=True)
                seuil_max = 0.90 if st.session_state.form_data["grut_dispo_pesage"] else 0.80
                st.caption(f"Seuil maximal toléré de la capacité grue : **{int(seuil_max*100)}%**")

                meteo_live = obtenir_meteo_amiens_live()
                if meteo_live["vent_j0"] > 36:
                    st.error(f"❌ **VENT SUPÉRIEUR À 36 km/h ({meteo_live['vent_j0']} km/h) : LE PERMIS GRUTAGE EST BLOQUÉ PAR LE SYSTÈME.**")

                st.info("✍️ **Signatures Automatiques requis :** Chef de Manœuvre + Élingueur + Grutier + DO P&G + Casque Rouge.")
                st.divider()

            # --- 6. PERMIS ESPACE CONFINÉ ---
            if st.session_state.form_data["p_confine"]:
                has_spe = True
                st.info("🦺 **PERMIS ENTRÉE EN ESPACE CONFINÉ (CBA 105)**")
                st.warning("🥽 **EPI Obligatoire :** Masque Auto-sauveteur de type M20 à la ceinture.")

                st.session_state.form_data["conf_lieu"] = st.text_input("Lieu précis de l'entrée en espace confiné :", value=st.session_state.form_data["conf_lieu"])
                st.session_state.form_data["conf_troudhomme_610"] = st.checkbox("Trou d'homme >= 610 mm", value=True)
                if not st.session_state.form_data["conf_troudhomme_610"]:
                    st.error("🚨 **Plan de secours spécifique CATEC requis (Trou d'homme < 610mm).**")

                st.markdown("##### Mesures Atmosphériques Préalables")
                cm1, cm2, cm3 = st.columns(3)
                with cm1: st.session_state.form_data["conf_o2"] = st.number_input("Niveau d'Oxygène O2 (19.5% - 23.0%) :", value=20.9)
                with cm2: st.session_state.form_data["conf_co"] = st.number_input("Niveau Monoxyde CO (ppm) :", value=0.0)
                with cm3: st.session_state.form_data["conf_explo"] = st.number_input("Explosimétrie LEL (%) :", value=0.0)

                st.divider()

            # --- 7. TRAVAIL ÉLECTRIQUE ---
            if st.session_state.form_data["p_electrique"]:
                has_spe = True
                st.error("⚡ **PERMIS TRAVAUX ÉLECTRIQUES (NF C 18-510)**")
                st.warning("🔒 **Rappel :** Les travaux sous tension sont STRICTEMENT INTERDITS. Les travaux au voisinage doivent être validés.")

                st.session_state.form_data["elec_voisinage_nues"] = st.checkbox("Travail au voisinage de pièces nues sous tension", value=st.session_state.form_data["elec_voisinage_nues"])
                if st.session_state.form_data["elec_voisinage_nues"]:
                    st.error("🥽 **EPIs Spécifiques Voisinage requis :** Écran facial Arc-Flash (GS-ET-29 Class 2) + Vestes Arc-Flash EN ISO 11612 + Nappes et Tapis Isolants (EN 61112).")
                    st.session_state.form_data["elec_valideur_ei"] = st.text_input("Validation obligatoire E&I / PT E&I (B2V/H2V, BC/HC) :", value=st.session_state.form_data["elec_valideur_ei"])
                st.divider()

            # --- 8. CONSIGNATION LOTO (3 PHASES) ---
            if st.session_state.form_data["p_consignation"]:
                has_spe = True
                st.success("⚡ **PERMIS CONSIGNATION & SÉPARATION D'ÉNERGIES (LOTO)**")
                
                c_lo1, c_lo2 = st.columns(2)
                with c_lo1:
                    st.session_state.form_data["loto_methode_ouverture"] = st.selectbox("Méthode d'isolation ouverture de circuit :", ["2 vannes et vanne de drain", "2 vannes simples", "Vanne simple", "Vanne et désolidarisation", "Joint plein (PG)", "Joint plein et désolidarisation"])
                    st.session_state.form_data["loto_loc1"] = st.text_input("Localisation Point d'Isolation 1 :", value=st.session_state.form_data["loto_loc1"])
                with c_lo2:
                    st.session_state.form_data["loto_loc2"] = st.text_input("Localisation Point d'Isolation 2 :", value=st.session_state.form_data["loto_loc2"])
                st.divider()

            # --- 9. SYSTÈME À RISQUES / ATEX / CHIMIQUE ---
            if st.session_state.form_data["p_systeme_risque"]:
                has_spe = True
                st.error("☣️ **PERMIS SYSTÈMES À RISQUES / ATEX / CHIMIQUE PARTICULIER**")
                
                csr1, csr2, csr3 = st.columns(3)
                with csr1: st.session_state.form_data["sr_chimique_c1"] = st.checkbox("Chimique Classe 1 (BFA, HCl...)", value=True)
                with csr2: st.session_state.form_data["sr_fluide_dang"] = st.checkbox("Fluides Dangereux (Soude, Vapeur...)", value=False)
                with csr3: st.session_state.form_data["sr_atex"] = st.checkbox("Zone ATEX (Zone 0, 1, 2)", value=False)

                st.session_state.form_data["sr_epi_comb2"] = st.checkbox("Combinaison 2 pièces anti-acide + Bottes sous pantalon", value=True)
                st.info("✍️ **3 Signatures Spécifiques :** Intervenant Qualifié Système à Risques + Donneur d'Ordre P&G + Responsable Exploitation/Opérations.")
                st.divider()

            if not has_spe:
                st.success("✅ Aucun permis spécifique ou formulaire HRT supplémentaire requis.")

            c_back, c_next = st.columns(2)
            with c_back:
                if st.button("⬅️ Précédent"): st.session_state.step = 5; st.rerun()
            with c_next:
                if st.button("Suivant ➔", type="primary"): st.session_state.step = 7; st.rerun()

        # =====================================================
        # ÉTAPE 7 : SYNTHÈSE, PDF DIRECT & SIGNATURES
        # =====================================================
        elif current_step == 7:
            st.subheader("7. Synthèse Globale & Co-signatures Tactiles")

            st.markdown("<div class='status-pending'>⚠️ PERMIS EN ATTENTE DE VALIDATION BATCH (07h30)</div>", unsafe_allow_html=True)

            if st.session_state.form_data["is_subcontractor"]:
                st.warning(f"🤝 **Règle de Sous-traitance Active :** Signature du N2 Titulaire du PDP requise ({st.session_state.form_data['titulaire_n2']}).")

            st.write("##### 📊 Tableau Récapitulatif Synthétique des Risques")
            
            tableau_data = []
            if st.session_state.form_data["p_hauteur"]:
                tableau_data.append({"activite": "Travail en Hauteur / Nacelle", "risque": "Chute de hauteur", "prevention": "Casque Jugulaire + Harnais + CACES PEMP"})
            if st.session_state.form_data["p_toiture"]:
                tableau_data.append({"activite": "Accès Toiture", "risque": "Chute à travers toiture / Météo", "prevention": f"{st.session_state.form_data['toiture_protection']} + Travail en Binôme"})
            if st.session_state.form_data["p_points_chauds"]:
                tableau_data.append({"activite": "Point Chaud / Flamme", "risque": "Incendie / Brûlures", "prevention": f"Visière EN 166B + Gants Soudeur + Extincteurs ({st.session_state.form_data['chaud_extincteur1']}) + Ronde 1h"})
            if st.session_state.form_data["p_excavation"]:
                tableau_data.append({"activite": "Excavation / Tranchée", "risque": "Effondrement / Réseaux enterrés", "prevention": f"DICT Validée + Blindage (>1.30m: {st.session_state.form_data['excav_profondeur_130']})"})
            if st.session_state.form_data["p_grutage"]:
                tableau_data.append({"activite": "Grutage & Levage", "risque": "Chute de charge / Renversement", "prevention": f"Plan de Levage + Pesage automatique + Anémomètre (<36 km/h)"})
            if st.session_state.form_data["p_confine"]:
                tableau_data.append({"activite": "Espace Confiné", "risque": "Asphyxie / Anoxie", "prevention": f"Masque M20 + Contrôle O2 ({st.session_state.form_data['conf_o2']}%) + Standby"})
            if st.session_state.form_data["p_electrique"]:
                tableau_data.append({"activite": "Travail Électrique", "risque": "Arc Flash / Électrocution", "prevention": "Gants EN 60903 + Casque Isolant + Outillage 1000V"})
            if st.session_state.form_data["p_consignation"]:
                tableau_data.append({"activite": "Consignation LOTO", "risque": "Énergie résiduelle", "prevention": f"Méthode {st.session_state.form_data['loto_methode_ouverture']} + Cadenassage"})
            if st.session_state.form_data["p_systeme_risque"]:
                tableau_data.append({"activite": "Systèmes à Risques / ATEX", "risque": "Exposition chimique / Explosion", "prevention": "EPIs Anti-acide + Douche de sécurité + Accord Exploitation"})

            if not tableau_data:
                tableau_data.append({"activite": "Travaux Généraux PDP", "risque": "Risques standards chantier", "prevention": "EPIs de base P&G Amiens"})

            st.table(tableau_data)

            st.divider()

            # Signatures
            st.write("##### ✍️ Co-signatures Tactiles de l'Équipe")
            for idx, nom in enumerate(st.session_state.form_data["intervenants"]):
                st.write(f"✍️ **Signature Intervenant {idx+1} : {nom}** [ Signé sur borne ]")

            if st.session_state.form_data["is_subcontractor"]:
                st.write(f"✍️ **Signature Obligatoire N2 Titulaire du PDP : {st.session_state.form_data['titulaire_n2']}** [ Signé sur borne ]")

            st.divider()

            permis_temp = {
                "id": f"PT-2026-0928-0{len(st.session_state.permis_db)+1}",
                "date_travaux": st.session_state.form_data["date_str"],
                "societe": st.session_state.form_data["societe"],
                "pdp": st.session_state.form_data["pdp"],
                "mop": st.session_state.form_data["mop"],
                "is_subcontractor": st.session_state.form_data["is_subcontractor"],
                "titulaire_n2": st.session_state.form_data["titulaire_n2"],
                "n2": st.session_state.form_data["n2_nom"],
                "zone": st.session_state.form_data["lieu_pdp"],
                "emplacement": st.session_state.form_data["lieu_precision"],
                "statut": "EN_ATTENTE_BATCH",
                "heure": datetime.datetime.now().strftime("%H:%M"),
                "intervenants": list(st.session_state.form_data["intervenants"]),
                "permis_specifiques": ["Hauteur" if st.session_state.form_data["p_hauteur"] else "", "Toiture" if st.session_state.form_data["p_toiture"] else "", "Point Chaud" if st.session_state.form_data["p_points_chauds"] else ""],
                "derogations": [],
                "tableau_risques": tableau_data
            }

            pdf_bytes = generer_pdf_bytes(permis_temp)

            c_back, c_sub, c_pdf = st.columns([1, 2, 2])
            with c_back:
                if st.button("⬅️ Précédent"): st.session_state.step = 6; st.rerun()

            with c_pdf:
                st.download_button(
                    label="📄 TÉLÉCHARGER LE PERMIS PDF",
                    data=pdf_bytes,
                    file_name=f"Permis_P_and_G_{permis_temp['id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with c_sub:
                if st.button("🚀 SOUMETTRE LE PERMIS AU BATCH (07h30)", type="primary", use_container_width=True):
                    st.session_state.permis_db.append(permis_temp)
                    st.balloons(); st.success(f"Permis {permis_temp['id']} transmis avec succès !"); st.session_state.kiosk_mode = "HOME"

# ==============================================================================
# INTERFACE 2 : DDS BOARD & BATCH 07H30 (DO / HSE)
# ==============================================================================
elif role == "📊 DDS Board & Batch 07h30 (DO / HSE)":
    st.markdown("<div class='pg-header' style='background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);'><h2 style='margin:0;'>DDS BOARD & TABLEAU DE BORD DONNEUR D'ORDRE (DO)</h2></div>", unsafe_allow_html=True)

    if st.button("✅ VALIDER LE BATCH DE 07h30 (AUTORISER TOUS LES PERMIS)", type="primary"):
        for p in st.session_state.permis_db: p["statut"] = "VALIDÉ"
        st.success("Fournée quotidienne validée ! Les permis sont officiellement actifs.")

    for pt in st.session_state.permis_db:
        with st.expander(f"Permis {pt['id']} - {pt['societe']} ({pt['statut']})"):
            st.write(f"**Zone :** {pt['zone']} | **N2 :** {pt['n2']}")
            pdf_valid_bytes = generer_pdf_bytes(pt)
            st.download_button("📄 Télécharger PDF Officiel", data=pdf_valid_bytes, file_name=f"Permis_{pt['id']}.pdf", mime="application/pdf", key=f"btn_{pt['id']}")

# ==============================================================================
# INTERFACE 3 : INSPECTION TERRAIN QR CODE (CASQUE ROUGE)
# ==============================================================================
else:
    st.markdown("<div class='pg-header' style='background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);'><h2 style='margin:0;'>AUDIT TERRAIN & SCAN QR CODE — CASQUE ROUGE</h2></div>", unsafe_allow_html=True)

    if st.session_state.permis_db:
        pt_sel = st.selectbox("Sélectionner un permis scanné sur zone :", [p["id"] for p in st.session_state.permis_db])
        p = next(p for p in st.session_state.permis_db if p["id"] == pt_sel)
        
        st.write(f"### Permis Ref : {p['id']} ({p['statut']})")
        st.write(f"**Entreprise :** {p['societe']} | **PDP :** {p['pdp']}")
        st.write(f"**Signataires :** {', '.join(p['intervenants'])}")
        
        st.table(p.get("tableau_risques", []))
        
        if st.button("✍️ Valider la Ronde de Sécurité Point Chaud (60 min)"):
            st.success("Ronde de sécurité validée et horodatée par le Casque Rouge.")
    else:
        st.info("Aucun permis émis pour le moment. Veuillez créer un permis sur la borne Kiosk.")
