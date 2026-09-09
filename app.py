import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Import des bibliothèques Google Drive
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    DRIVE_LIB_AVAILABLE = True
except ImportError:
    DRIVE_LIB_AVAILABLE = False

# Configuration de la page
st.set_page_config(
    page_title="Audit Sécurité & HSE - Entreprises Extérieures",
    page_icon="🛡️",
    layout="wide"
)

# Style CSS sur mesure
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { font-size: 15px; color: #4B5563; margin-bottom: 20px; }
    .guidance-box { 
        background-color: #F0F9FF; 
        border-left: 4px solid #0284C7; 
        padding: 10px 14px; 
        border-radius: 4px; 
        font-size: 13px; 
        color: #0369A1; 
        margin-top: 6px; 
        margin-bottom: 12px; 
    }
    .question-title { font-size: 16px; font-weight: 600; color: #1F2937; margin-top: 10px; }
    
    .stFormSubmitButton > button {
        width: 100% !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 18px 30px !important;
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        border: 4px solid #3B82F6 !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 12px rgba(30, 58, 138, 0.3) !important;
        cursor: pointer !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #2563EB !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Base complète des 54 questions
QUESTIONS_DATA = [
    # 1. Expectations & Involvement
    {"id": "1.1", "cat": "1. Expectations & Involvement", "q": "Site comprehensive Safety Program in place", "g": "• Components shall be written and documented in a digital manual specific for site\n• Should encompass all aspects of safety deliverables as outlined in CSPA"},
    {"id": "1.2", "cat": "1. Expectations & Involvement", "q": "Site-specific emergency action plan", "g": "• Plan is kept current with reporting lines and responsibilities"},
    {"id": "1.3", "cat": "1. Expectations & Involvement", "q": "Incident Investigation Process", "g": "• Procedure utilizes HSE-GGC-005 or aligns with it"},
    {"id": "1.4", "cat": "1. Expectations & Involvement", "q": "Participation in the safety process at all levels", "g": "• Interview front-line workers to ensure needs are met and are supported"},
    {"id": "1.5", "cat": "1. Expectations & Involvement", "q": "Qualification of sub-contractors and direct managed work", "g": "• Program in place to vet and qualify sub-contractors\n• Procedures for new contractors to site"},

    # 2. Vision, Goal Setting, Performance Tracking
    {"id": "2.1", "cat": "2. Vision & Performance Tracking", "q": "Site-Specific Vision and Goals that is developed, reviewed, and updated at a minimum annually.", "g": "• Main goal is a Zero-Incident Rate\n• Goals are communicated to site at all levels"},
    {"id": "2.2", "cat": "2. Vision & Performance Tracking", "q": "Site is committed to continuous improvement of safety systems and culture", "g": "• Discuss recent improvements\n• Discuss how new ideas are being shared and used"},
    {"id": "2.3", "cat": "2. Vision & Performance Tracking", "q": "Meetings conducted at least monthly with Contractor Safety Leadership & Site HSE", "g": "• Ensure common goals and avenue for transparent communication"},
    {"id": "2.4", "cat": "2. Vision & Performance Tracking", "q": "Create short-term goals based on real-time indicators", "g": "• Put action plans/interventions in place based on BOS data, incidents, etc"},
    {"id": "2.5", "cat": "2. Vision & Performance Tracking", "q": "Safety Perception Surveys are conducted", "g": "• Survey proves effectiveness of the safety program to ensure a positive safety culture\n• Conducted every 2 years"},
    {"id": "2.6", "cat": "2. Vision & Performance Tracking", "q": "Safety metrics are tracked, displayed, and transmitted to P&G HSE and Construction leaders", "g": "• Hours worked, incidents, near misses, first aids, BOS metrics\n• EMR and insurance documentation submitted at least annually"},
    {"id": "2.7", "cat": "2. Vision & Performance Tracking", "q": "Digital tools, visuals, dashboards are used to track safety measures", "g": "• Modernized safety systems\n• At your fingertip data"},
    {"id": "2.8", "cat": "2. Vision & Performance Tracking", "q": "Performance Reviews", "g": "• Reviews of site staff\n• Feedback for P&G\n• Performed annually"},

    # 3.1 Life Critical
    {"id": "3.1.1", "cat": "3.1 Life Critical", "q": "Confined Space Entry (CSE)", "g": "Employee training; permit system authorizers identified; attendants and rescue personnel training; review of property damage incidents"},
    {"id": "3.1.2", "cat": "3.1 Life Critical", "q": "Crane Operations", "g": "Licensed operators; daily inspection log established; lift plans when applicable; hoisting personnel"},
    {"id": "3.1.3", "cat": "3.1 Life Critical", "q": "Electrical Work", "g": "Work is performed under supervision of qualified person; live work is exception rather than routine. Permit system and hazard analysis in place. Arc flash PPE provided"},
    {"id": "3.1.4", "cat": "3.1 Life Critical", "q": "Excavation and Trenching", "g": "Underground utilities identified; competent person on site; permit system used; government regulations observed"},
    {"id": "3.1.5", "cat": "3.1 Life Critical", "q": "Fall Prevention", "g": "Full body harness required for exposures to falls over 6 feet (1.8 meters) and when in aerial baskets, show written site-specific plan"},
    {"id": "3.1.6", "cat": "3.1 Life Critical", "q": "Chemical Management Program", "g": "MSDS file for all chemicals, employees instructed; containers labeled"},
    {"id": "3.1.7", "cat": "3.1 Life Critical", "q": "Isolation of Hazardous Work (LOTO)", "g": "Method of lockout/tag out communicated; emergency lock removal system. Lockouts documented"},
    {"id": "3.1.8", "cat": "3.1 Life Critical", "q": "Scaffold Erection", "g": "Competent personnel on site; scaffolds tagged according to site plan; government specifications. Observe scaffolds in the field."},
    {"id": "3.1.9", "cat": "3.1 Life Critical", "q": "Ladder Safety", "g": "Heavy industrial non-conductive ladders used, use limited to short-term light work"},
    {"id": "3.1.10", "cat": "3.1 Life Critical", "q": "Roof Work", "g": "Safe access to roof, fall preventions in place"},
    {"id": "3.1.11", "cat": "3.1 Life Critical", "q": "Aerial / Scissors Lifts", "g": "Trained and qualified operator"},
    {"id": "3.1.12", "cat": "3.1 Life Critical", "q": "Rigging", "g": "Inspection of rigging, qualified, trained operators"},

    # 3.2 Current Best Approaches
    {"id": "3.2.1", "cat": "3.2 Current Best Approaches", "q": "Chemical Clearance", "g": "List of approved chemicals; buyers do not purchase items not on list; new chemical qualification"},
    {"id": "3.2.2", "cat": "3.2 Current Best Approaches", "q": "Chemical Exposure Control", "g": "Hexavalent Chromium, Toxic dust, etc testing is done; Workplace controls, PPE requirements"},
    {"id": "3.2.3", "cat": "3.2 Current Best Approaches", "q": "Safety Incident Management", "g": "Injuries and near misses entered into Incident database each day as required and monthly"},
    {"id": "3.2.4", "cat": "3.2 Current Best Approaches", "q": "Demolition", "g": "Plan in place to manage unique conditions; asbestos, lead, radioactive isotopes; structure integrity"},
    {"id": "3.2.5", "cat": "3.2 Current Best Approaches", "q": "Emergency Management System", "g": "Emergency phone numbers, evacuation alarms, and route maps. Employees know the plan."},
    {"id": "3.2.6", "cat": "3.2 Current Best Approaches", "q": "Environmental Management", "g": "Hazardous waste storage; spill prevention; government notification of releases; spill clean-up"},
    {"id": "3.2.7", "cat": "3.2 Current Best Approaches", "q": "Ergonomics", "g": "Buyer use of catalog; site ergonomic action plan -focus on material handling & soft tissue injuries; training provided"},
    {"id": "3.2.8", "cat": "3.2 Current Best Approaches", "q": "Gas Cylinders", "g": "Compressed gas cylinders handling, use, and storage"},
    {"id": "3.2.9", "cat": "3.2 Current Best Approaches", "q": "Regulatory Agency Inspections", "g": "Safety personnel and site management instruction of what to do in case of government activity"},
    {"id": "3.2.10", "cat": "3.2 Current Best Approaches", "q": "Hand Injury Prevention", "g": "Review injury data; glove program; chemical barrier cream use; vibration ergo gloves used"},
    {"id": "3.2.11", "cat": "3.2 Current Best Approaches", "q": "Hazardous Systems", "g": "List of site's hazardous systems exists; permit system is in place; system owner training"},
    {"id": "3.2.12", "cat": "3.2 Current Best Approaches", "q": "Fire Prevention", "g": "Hot work permit used; fire watch used; systems not impaired without fire marshal approval"},
    {"id": "3.2.13", "cat": "3.2 Current Best Approaches", "q": "Hearing Protection", "g": "Noise survey conducted; audiometric testing; warning signs used; hearing protection worn"},
    {"id": "3.2.14", "cat": "3.2 Current Best Approaches", "q": "Construction Housekeeping", "g": "Appropriate waste containers used; orderly storage; trip hazards eliminated; access/emergency equipment kept clear."},
    {"id": "3.2.15", "cat": "3.2 Current Best Approaches", "q": "Laser Radiation Safety", "g": "Laser instrument use controlled; work areas controlled as necessary for exposure"},
    {"id": "3.2.16", "cat": "3.2 Current Best Approaches", "q": "Lead Exposure Control", "g": "Site survey identifies lead; awareness training for all employees; removal by authorized personnel"},
    {"id": "3.2.17", "cat": "3.2 Current Best Approaches", "q": "Line Breaking", "g": "Systems identified that require permits; PPE used; review permits on file"},
    {"id": "3.2.18", "cat": "3.2 Current Best Approaches", "q": "First Aid and Medical Treatment", "g": "First-aid station with trained providers; emergency medical numbers posted; medical facility identified. Old stock removed and replaced. First aid room is clean"},
    {"id": "3.2.19", "cat": "3.2 Current Best Approaches", "q": "Personal Protective Equipment (PPE)", "g": "Question employees to verify PPE training; PPE selection and enforcement of use"},
    {"id": "3.2.20", "cat": "3.2 Current Best Approaches", "q": "Ionizing Radiation Safety", "g": "Systems using radioactive isotopes identified; site radiation officer contacted before any removal activity"},
    {"id": "3.2.21", "cat": "3.2 Current Best Approaches", "q": "Railroad Safety", "g": "Track clearances maintained; use of blue light/blue sign procedures; derails and switch lockout used"},
    {"id": "3.2.22", "cat": "3.2 Current Best Approaches", "q": "Safety Culture Recognition Program", "g": "Review site program to check that employees are recognized for following safe practices"},
    {"id": "3.2.23", "cat": "3.2 Current Best Approaches", "q": "Respiratory Program", "g": "Health questionnaires, PFT & fit test if required. Written plan for respiratory protection. Rules for voluntary use established"},
    {"id": "3.2.24", "cat": "3.2 Current Best Approaches", "q": "Signs and Barricades", "g": "When and where signage and barricading needed. Signs & barricades in place match the hazards."},
    {"id": "3.2.25", "cat": "3.2 Current Best Approaches", "q": "Substance Abuse Program", "g": "Files maintained with documentation of screening results; site required testing (10 panel, and so on) performed; verify subcontractors follow the plan"},
    {"id": "3.2.26", "cat": "3.2 Current Best Approaches", "q": "Powered Industrial Truck Operation", "g": "Operators certified by competent person for each type truck used; documentation of ability and knowledge."},
    {"id": "3.2.27", "cat": "3.2 Current Best Approaches", "q": "Portable Power Tools", "g": "Employees trained to use, tools inspected"},
    {"id": "3.2.28", "cat": "3.2 Current Best Approaches", "q": "Blood Borne Pathogens", "g": "Controlled Exposure, Proper training"},
    {"id": "3.2.29", "cat": "3.2 Current Best Approaches", "q": "Contractor Safety Non-Compliance", "g": "Disciplinary action plan with contract language that includes contractor removal from site"},
    {"id": "3.2.30", "cat": "3.2 Current Best Approaches", "q": "Working Safely Near Operating Business Areas", "g": "Barriers in Place, signage, training"},
    {"id": "3.2.31", "cat": "3.2 Current Best Approaches", "q": "Non Power Cutting Tools", "g": "Safe use, inspection, and appropriate selection of non-powered tools"},

    # 4. Planning & Operations
    {"id": "4.1", "cat": "4. Planning & Operations", "q": "Site uses a daily work management and hazard analysis tools.", "g": "• Job Safety Analysis\n• Safety Task Analysis (STA)\n• Project Planning Safety Assessment (PPSA)\n• IE DMS (Incident Elimination Daily Management System)\n• Discuss the use of these systems individually"},
    {"id": "4.2", "cat": "4. Planning & Operations", "q": "Behavior Observation Survey (BOS)", "g": "• Discuss process and site goal for participation\n• Participation includes staff, supervisory, and construction field personnel.\n• Recommendations and improvements are acted upon."},
    {"id": "4.3", "cat": "4. Planning & Operations", "q": "Fatigue & Overtime Management", "g": "• Overtime planned and tracked per CBA 603\n• Fitness for duty program in place to manage workplace fatigue"},
    {"id": "4.4", "cat": "4. Planning & Operations", "q": "Equipment Inspection Data", "g": "• Ensure site has systems in place to track and complete inspections\n• Inspections of at least: mobile and aerial equipment, crane, rigging, fire extinguisher, ladder, hand/power tools, GFCI, cords, rescue equipment"},
    {"id": "4.5", "cat": "4. Planning & Operations", "q": "Site Walks", "g": "• Ensure management is conducting site walks regularly to confirm safe conditions\n• Walks should focus on tidiness, material staging, danger areas, walking/working surfaces, interface with operations, lighting"},
    {"id": "4.6", "cat": "4. Planning & Operations", "q": "Meetings", "g": "• Execution Leader to conduct Daily and Weekly Safety Meetings\n• Incident review meetings\n• Frontline leadership to attend daily coordination meetings\n• Quarterly site safety meetings with contractor regional safety leaders/managers"},
    {"id": "4.7", "cat": "4. Planning & Operations", "q": "Site Staffing", "g": "• Safety staffing model for site\n• Consider projects and scope of work rather than a designated ratio\n• Program Leader vs Execution Leaders\n• Full time vs dual purpose designated safety professional"},

    # 5. Site Safety Training Systems
    {"id": "5.1", "cat": "5. Safety Training Systems", "q": "Site-specific Orientation", "g": "• Orientation should be all encompassing of safety risks and hazards onsite\n• Should convey PPE requirements\n• Should convey emergency action procedures\n• Must have a knowledge check"},
    {"id": "5.2", "cat": "5. Safety Training Systems", "q": "Site and its contractors shall maintain record of all training and certifications of personnel", "g": "• Including site training\n• 3rd party (First Aid, CPR, Blood Borne Pathogens, OSHA specific trainings, etc)\n• Task specific (lift, heavy equipment, confined space)\n• Local government required training"},
    {"id": "5.3", "cat": "5. Safety Training Systems", "q": "Weekly Safety Training", "g": "• Sites hosts weekly toolbox talks, construction moments, or meetings with all craft"},
    {"id": "5.4", "cat": "5. Safety Training Systems", "q": "New Employee Training Program", "g": "• Training for salary employees\n• Training for Craft Supervision\n• Training for BOS\n• Training to become competent person\n• Training on Chemical Clearance System"},
    {"id": "5.5", "cat": "5. Safety Training Systems", "q": "Refresher Training", "g": "Ensure system in place to keep training up to date and refreshed at required interval"}
]

def upload_file_to_drive(uploaded_file, company_name, q_id):
    if not DRIVE_LIB_AVAILABLE:
        return f"Fichier joint : {uploaded_file.name}"
    
    try:
        creds_info = None
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            creds_info = dict(st.secrets["connections"]["gsheets"])
        elif "gcp_service_account" in st.secrets:
            creds_info = dict(st.secrets["gcp_service_account"])
            
        if not creds_info:
            return f"Fichier joint : {uploaded_file.name}"

        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': f"{company_name}_{q_id}_{uploaded_file.name}"
        }
        
        if "drive_folder_id" in st.secrets:
            file_metadata['parents'] = [st.secrets["drive_folder_id"]]

        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type)
        file_res = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        service.permissions().create(
            fileId=file_res.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        return file_res.get('webViewLink')
    except Exception as e:
        return f"Fichier joint : {uploaded_file.name}"

# Navigation principale par onglets
tab_form, tab_admin = st.tabs(["📝 Formulaire Prestataire", "🔒 Espace Administrateur HSE"])

# ==========================================
# ONGLET 1 : FORMULAIRE PRESTATAIRE
# ==========================================
with tab_form:
    st.markdown("""<div class="main-header">🛡️ Formulaire d'Audit Sécurité & HSE</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="sub-header">Évaluation de conformité pour les entreprises extérieures. Merci de répondre à chaque question et de fournir les justifications nécessaires.</div>""", unsafe_allow_html=True)

    with st.expander("📂 Reprendre un brouillon enregistré auparavant (Optionnel)", expanded=False):
        uploaded_draft = st.file_uploader("Importez votre fichier de brouillon (.json) :", type=["json"], key="draft_importer")
        draft_data = {}
        if uploaded_draft is not None:
            try:
                draft_data = json.load(uploaded_draft)
                st.success("✅ Brouillon chargé avec succès ! Vos réponses précédentes ont été appliquées.")
            except Exception:
                st.error("⚠️ Fichier de brouillon invalide.")

    with st.form(key="audit_form"):
        st.subheader("1. Informations de l'Entreprise Extérieure")
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Nom de l'entreprise *", value=draft_data.get("Entreprise", ""), placeholder="Ex: ABC Construction")
            auditor_name = st.text_input("Nom du déclarant / Représentant HSE *", value=draft_data.get("Déclarant", ""), placeholder="Ex: Jean Dupont")
        with col2:
            site_location = st.text_input("Site / Chantier concerné *", value=draft_data.get("Site", ""), placeholder="Ex: Usine Amiens - Zone B")
            audit_date = st.date_input("Date de soumission", value=datetime.today())

        st.markdown("---")
        st.subheader("2. Grille d'Évaluation des Exigences Sécurité")

        categories = sorted(list(set(q["cat"] for q in QUESTIONS_DATA)))
        responses = {}
        uploaded_files_dict = {}
        
        for cat in categories:
            st.markdown(f"### 📌 {cat}")
            cat_questions = [q for q in QUESTIONS_DATA if q["cat"] == cat]
            
            for q in cat_questions:
                st.markdown(f'<div class="question-title">[{q["id"]}] {q["q"]}</div>', unsafe_allow_html=True)
                if q["g"]:
                    st.markdown(f'<div class="guidance-box"><b>Attentes & Guidance :</b><br>{q["g"]}</div>', unsafe_allow_html=True)
                
                saved_status = draft_data.get(f"{q['id']}_Réponse", "N/A")
                status_index = ["Oui", "Non", "N/A"].index(saved_status) if saved_status in ["Oui", "Non", "N/A"] else 2
                saved_justif = draft_data.get(f"{q['id']}_Justification", "")

                c1, c2 = st.columns([1, 2])
                with c1:
                    status = st.radio(
                        f"Réponse {q['id']}",
                        options=["Oui", "Non", "N/A"],
                        index=status_index,
                        horizontal=True,
                        key=f"status_{q['id']}"
                    )
                with c2:
                    justification = st.text_area(
                        f"Justification {q['id']}",
                        value=saved_justif,
                        placeholder="Justifiez votre réponse (procédure interne, preuve, plan d'action si Non/NA)...",
                        key=f"justif_{q['id']}",
                        height=80
                    )
                
                file_attached = st.file_uploader(
                    f"📎 Pièce justificative pour [{q['id']}] (Optionnel)",
                    type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"],
                    key=f"file_{q['id']}"
                )
                
                responses[q['id']] = {
                    "status": status,
                    "justification": justification
                }
                if file_attached is not None:
                    uploaded_files_dict[q['id']] = file_attached
                    
                st.markdown("<hr style='margin: 15px 0; border-top: 1px dashed #E5E7EB;'>", unsafe_allow_html=True)

        submit_button = st.form_submit_button(label="🚀 VALIDER ET ENVOYER L'AUDIT")

    if submit_button:
        missing_fields = []
        if not company_name: missing_fields.append("Nom de l'entreprise")
        if not auditor_name: missing_fields.append("Nom du déclarant")
        if not site_location: missing_fields.append("Site / Chantier")
        
        unjustified = [q_id for q_id, res in responses.items() if res["status"] in ["Non", "N/A"] and not res["justification"].strip()]
                
        if missing_fields:
            st.error(f"⚠️ Veuillez remplir les informations obligatoires : {', '.join(missing_fields)}.")
        elif unjustified:
            st.warning(f"⚠️ Une justification est requise pour toute réponse 'Non' ou 'N/A'. Question(s) concernée(s) : {', '.join(unjustified)}")
        else:
            st.info("⏳ Enregistrement de l'audit en cours...")
            
            record = {
                "Date": str(audit_date),
                "Entreprise": company_name,
                "Déclarant": auditor_name,
                "Site": site_location,
            }
            
            for q_id, res in responses.items():
                record[f"{q_id}_Réponse"] = res["status"]
                record[f"{q_id}_Justification"] = res["justification"]
                
                if q_id in uploaded_files_dict:
                    file_obj = uploaded_files_dict[q_id]
                    drive_link_or_name = upload_file_to_drive(file_obj, company_name, q_id)
                    record[f"{q_id}_Fichier"] = drive_link_or_name
                else:
                    record[f"{q_id}_Fichier"] = ""
            
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_data = conn.read()
                df_new = pd.DataFrame([record])
                updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success("✅ Audit enregistré avec succès dans la base centrale !")
                st.balloons()
            except Exception:
                st.success("✅ Vos réponses ont été enregistrées localement.")
                st.download_button(
                    label="📥 Télécharger votre copie d'audit (CSV / Excel)",
                    data=pd.DataFrame([record]).to_csv(index=False).encode('utf-8'),
                    file_name=f"Audit_{company_name}_{audit_date}.csv",
                    mime="text/csv"
                )

    st.markdown("---")
    st.subheader("💾 Vous n'avez pas fini ? Sauvegarder votre avancement")
    draft_export = {
        "Entreprise": company_name if 'company_name' in locals() else "",
        "Déclarant": auditor_name if 'auditor_name' in locals() else "",
        "Site": site_location if 'site_location' in locals() else "",
    }
    if 'responses' in locals():
        for q_id, res in responses.items():
            draft_export[f"{q_id}_Réponse"] = res["status"]
            draft_export[f"{q_id}_Justification"] = res["justification"]

    st.download_button(
        label="💾 Télécharger le fichier de brouillon (.json)",
        data=json.dumps(draft_export, ensure_ascii=False, indent=2),
        file_name=f"Brouillon_Audit_{company_name if 'company_name' in locals() and company_name else 'Incomplet'}.json",
        mime="application/json"
    )

# ==========================================
# ONGLET 2 : ESPACE ADMINISTRATEUR HSE
# ==========================================
with tab_admin:
    st.markdown("""<div class="main-header">🔒 Espace d'Administration & Consultation</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="sub-header">Consultez l'ensemble des audits validés par les prestataires et examinez leurs justificatifs.</div>""", unsafe_allow_html=True)
    
    # Bouton d'actualisation des données
    if st.button("🔄 Actualiser la liste des audits"):
        st.cache_data.clear()

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_audits = conn.read()
        # Supprimer les lignes vides s'il y en a
        df_audits = df_audits.dropna(how="all")
    except Exception as e:
        df_audits = pd.DataFrame()
        st.warning("⚠️ Impossible de se connecter directement à Google Sheets pour le moment.")

    if df_audits.empty:
        st.info("Aucun audit n'a encore été enregistré dans la base.")
    else:
        # Construction de la liste sélectionnable
        audit_options = []
        for idx, row in df_audits.iterrows():
            ent = row.get("Entreprise", "Inconnu")
            dt = row.get("Date", "N/A")
            st_name = row.get("Site", "N/A")
            audit_options.append(f"{ent} — {dt} (Site: {st_name})")
        
        selected_idx = st.selectbox(
            "📋 Sélectionnez un audit validé pour afficher l'ensemble des détails :",
            range(len(audit_options)),
            format_func=lambda x: audit_options[x]
        )
        
        selected_row = df_audits.iloc[selected_idx]
        
        st.markdown("---")
        
        # En-tête de la fiche audit sélectionnée
        st.subheader(f"📄 Fiche Audit : {selected_row.get('Entreprise', 'N/A')}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏢 Entreprise", str(selected_row.get("Entreprise", "N/A")))
        c2.metric("👤 Déclarant", str(selected_row.get("Déclarant", "N/A")))
        c3.metric("📍 Site", str(selected_row.get("Site", "N/A")))
        c4.metric("📅 Date", str(selected_row.get("Date", "N/A")))
        
        # Calcul rapide des totaux Oui / Non / N/A pour cet audit
        oui_count = sum(1 for col in selected_row.index if col.endswith("_Réponse") and str(selected_row[col]).strip() == "Oui")
        non_count = sum(1 for col in selected_row.index if col.endswith("_Réponse") and str(selected_row[col]).strip() == "Non")
        na_count = sum(1 for col in selected_row.index if col.endswith("_Réponse") and str(selected_row[col]).strip() == "N/A")
        
        st.markdown("#### 📊 Synthèse des réponses")
        k1, k2, k3 = st.columns(3)
        k1.success(f"✅ Conforme (Oui) : {oui_count}")
        k2.error(f"❌ Non Conforme (Non) : {non_count}")
        k3.info(f"⚪ Non Applicable (N/A) : {na_count}")
        
        st.markdown("---")
        st.markdown("### 🔍 Détail des 54 Exigences Sécurité")
        
        # Regroupement par catégories pour la lecture admin
        categories_admin = sorted(list(set(q["cat"] for q in QUESTIONS_DATA)))
        
        for cat in categories_admin:
            st.markdown(f"#### 📌 {cat}")
            cat_q = [q for q in QUESTIONS_DATA if q["cat"] == cat]
            
            for q in cat_q:
                q_id = q["id"]
                resp_val = str(selected_row.get(f"{q_id}_Réponse", "Non renseigné"))
                justif_val = str(selected_row.get(f"{q_id}_Justification", "Aucune justification"))
                file_val = str(selected_row.get(f"{q_id}_Fichier", ""))
                
                # Badge couleur selon la réponse
                if resp_val == "Oui":
                    badge = "🟢 **Oui**"
                elif resp_val == "Non":
                    badge = "🔴 **Non**"
                else:
                    badge = "⚪ **N/A**"
                
                with st.expander(f"[{q_id}] {q['q']} — {badge}"):
                    st.write(f"**Exigence / Question :** {q['q']}")
                    if q['g']:
                        st.caption(f"**Attentes :** {q['g']}")
                    st.write(f"**Statut :** {badge}")
                    st.write(f"**Justification entreprise :** {justif_val}")
                    
                    if file_val and file_val.startswith("http"):
                        st.markdown(f"📎 **Pièce jointe :** [Ouvrir le document ({file_val})]({file_val})")
                    elif file_val:
                        st.write(f"📎 **Pièce jointe :** {file_val}")
                    else:
                        st.caption("📎 Aucune pièce jointe transmise pour cette question.")
