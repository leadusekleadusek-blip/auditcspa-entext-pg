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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS sur mesure pour améliorer la lisibilité, les cartes de questions et la mise en page
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { font-size: 15px; color: #4B5563; margin-bottom: 20px; }
    
    /* Carte de question avec bordure marquée et ombre */
    .question-card {
        background-color: #FFFFFF;
        border: 2px solid #CBD5E1;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Titre de question plus gros et plus lisible */
    .question-title-big {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        margin-bottom: 5px;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 6px;
    }
    
    .guidance-box { 
        background-color: #F0F9FF; 
        border-left: 4px solid #0284C7; 
        padding: 12px 16px; 
        border-radius: 6px; 
        font-size: 14px; 
        color: #0369A1; 
        margin-top: 8px; 
        margin-bottom: 16px; 
    }
    
    .stButton > button {
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 16px 28px !important;
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        border: 3px solid #3B82F6 !important;
        border-radius: 10px !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background-color: #2563EB !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Base complète des 54 questions réparties sur 5 grands thèmes
QUESTIONS_DATA = [
    # Thème 1 : Attentes & Engagement
    {"id": "1.1", "theme": "1. Attentes & Engagement", "cat": "1. Attentes & Engagement", "q": "Programme de sécurité complet en place sur le site", "g": "• Manuel numérique spécifique au site rédigé et documenté\n• Doit englober tous les aspects des livrables sécurité définis dans le cahier des charges"},
    {"id": "1.2", "theme": "1. Attentes & Engagement", "cat": "1. Attentes & Engagement", "q": "Plan d'action d'urgence spécifique au site", "g": "• Plan tenu à jour incluant la chaîne d'alerte et les responsabilités de chacun"},
    {"id": "1.3", "theme": "1. Attentes & Engagement", "cat": "1. Attentes & Engagement", "q": "Processus d'analyse et d'enquête sur les incidents", "g": "• Procédure conforme aux exigences HSE du site"},
    {"id": "1.4", "theme": "1. Attentes & Engagement", "cat": "1. Attentes & Engagement", "q": "Implication du personnel à tous les niveaux dans la sécurité", "g": "• Échanger avec le personnel de terrain pour s'assurer que leurs besoins sont pris en compte"},
    {"id": "1.5", "theme": "1. Attentes & Engagement", "cat": "1. Attentes & Engagement", "q": "Qualification des sous-traitants et des prestations gérées", "g": "• Système de qualification préalable des sous-traitants\n• Procédure d'accueil pour tout nouveau prestataire"},

    # Thème 2 : Vision & Suivi de la Performance
    {"id": "2.1", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Vision et objectifs sécurité spécifiques au site (revus annuellement)", "g": "• Objectif principal : zéro accident\n• Objectifs communiqués à l'ensemble du personnel"},
    {"id": "2.2", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Engagement dans l'amélioration continue de la culture sécurité", "g": "• Partage des retours d'expérience et déploiement de nouvelles initiatives sécurité"},
    {"id": "2.3", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Réunions mensuelles minimum entre le responsable sécurité prestataire et le HSE site", "g": "• Garantir des objectifs communs et une communication fluide"},
    {"id": "2.4", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Création d'objectifs à court terme basés sur les indicateurs terrain", "g": "• Mettre en place des actions préventives basées sur les observations et presqu'accidents"},
    {"id": "2.5", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Enquêtes de perception de la sécurité réalisées", "g": "• Évaluation de l'efficacité du programme sécurité (réalisée tous les 2 ans)"},
    {"id": "2.6", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Suivi, affichage et transmission des indicateurs sécurité au service HSE", "g": "• Heures travaillées, accidents, presqu'accidents, soins infirmiers, visites d'observation"},
    {"id": "2.7", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Utilisation d'outils numériques et tableaux de bord de suivi", "g": "• Numérisation du suivi sécurité pour un accès immédiat aux données"},
    {"id": "2.8", "theme": "2. Vision & Suivi de la Performance", "cat": "2. Vision & Suivi de la Performance", "q": "Revues de performance sécurité annuelles", "g": "• Bilan annuel du personnel et partage des retours d'expérience"},

    # Thème 3 : Risques Critiques & Meilleures Pratiques
    {"id": "3.1.1", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Intervention en Espaces Confinés", "g": "Formation du personnel, permis de pénétrer, surveillant qualifié et moyens de secours"},
    {"id": "3.1.2", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Opérations de Levage et Grutage", "g": "Conducteurs certifiés (CACES), contrôle quotidien des engins, plan de levage si nécessaire"},
    {"id": "3.1.3", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Travaux Électriques et Habilitations", "g": "Personnel habilité, travaux sous tension exceptionnels et encadrés, EPI contre le risque d'arc électrique"},
    {"id": "3.1.4", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Fouilles, Excavations et Tranchées", "g": "Repérage des réseaux enterrés, personne compétente sur site, permis de fouille"},
    {"id": "3.1.5", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Prévention des Chutes de Hauteur", "g": "Port du harnais obligatoire dès 1,80 m et en nacelle, plan de prévention antichute écrit"},
    {"id": "3.1.6", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Gestion des Produits Chimiques", "g": "Fiches de Données de Sécurité (FDS) disponibles, étiquetage réglementaire des produits"},
    {"id": "3.1.7", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Consignation et Condamnation d'Énergies (LOTO)", "g": "Procédure LOTO formalisée, condamnation par cadenas individuel, traçabilité des opérations"},
    {"id": "3.1.8", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Montage et Utilisation d'Échafaudages", "g": "Montage par du personnel qualifié, vérification quotidienne et affichage des panneaux de conformité"},
    {"id": "3.1.9", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Utilisation Sécurisée des Échelles", "g": "Échelles industrielles isolantes, usage limité aux accès ou travaux ponctuels très légers"},
    {"id": "3.1.10", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Travaux sur Toitures", "g": "Accès sécurisés, balisage et garde-corps ou lignes de vie en place"},
    {"id": "3.1.11", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Nacelles et Plateformes Élévatrices (PEMPS)", "g": "Conducteurs formés et titulaires de l'autorisation de conduite (CACES)"},
    {"id": "3.1.12", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.1 Risques Vitaux (Life Critical)", "q": "Élingage et Matériel de Levage", "g": "Inspection périodique des élingues et accessoires, élingueurs qualifiés"},
    {"id": "3.2.1", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Validation Préalable des Produits Chimiques", "g": "Liste des produits autorisés sur site, interdiction des produits non validés au préalable"},
    {"id": "3.2.2", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Contrôle des Expositions Chimiques et Poussières", "g": "Mesures de prévention (extraction, ventilation) et port d'EPI adaptés (chrome, poussières)"},
    {"id": "3.2.3", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Signalement des Incidents et Presqu'accidents", "g": "Enregistrement rapide de tous les événements sécurité dans la base de données"},
    {"id": "3.2.4", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Travaux de Démolition", "g": "Plan de démolition ciblé (gestion de l'amiante, du plomb, stabilité des structures)"},
    {"id": "3.2.5", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Gestion des Situations d'Urgence", "g": "Consignes d'urgence, numéros utiles et plans d'évacuation connus des intervenants"},
    {"id": "3.2.6", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Gestion de l'Environnement et des Déchets", "g": "Stockage conforme des déchets dangereux, kits anti-pollution disponibles"},
    {"id": "3.2.7", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Ergonomie et Manutention Manuelle", "g": "Matériel d'aide à la manutention, sensibilisation aux gestes et postures pour éviter les TMS"},
    {"id": "3.2.8", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Stockage et Manipulation des Bouteilles de Gaz", "g": "Stockage vertical, bouteilles arrimées et chapeaux de protection en place"},
    {"id": "3.2.9", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Inspections des Organismes Officiels (Inspection du Travail, etc.)", "g": "Procédure d'accueil et d'accompagnement définie en cas de contrôle externe"},
    {"id": "3.2.10", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Prévention des Blessures aux Mains", "g": "Port de gants adaptés au risque, utilisation de cutters de sécurité"},
    {"id": "3.2.11", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Systèmes et Équipements à Risques", "g": "Inventaire des équipements à risques, délivrance de permis de travail spécifiques"},
    {"id": "3.2.12", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Prévention des Incendies (Permis de Feu)", "g": "Délivrance systématique d'un permis de feu pour points chauds et présence d'un piquet d'incendie"},
    {"id": "3.2.13", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Protection contre le Bruit", "g": "Signalisation des zones bruyantes et port obligatoire des protections auditives"},
    {"id": "3.2.14", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Tenue et Propreté du Chantier", "g": "Rangement quotidien, suppression des risques de trébuchement, voies de circulation dégagées"},
    {"id": "3.2.15", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Sécurité des Rayonnements Laser", "g": "Mise en œuvre sécurisée des outils laser et balisage de la zone d'exposition"},
    {"id": "3.2.16", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Prévention de l'Exposition au Plomb", "g": "Repérage préalable, information des salariés et retrait par du personnel qualifié"},
    {"id": "3.2.17", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Ouverture de Tuyauteries et Lignes (Line Breaking)", "g": "Permis spécifique, vidange préalable et port des EPI adaptés"},
    {"id": "3.2.18", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Premiers Secours et Soins d'Urgence", "g": "Trousses de secours approvisionnées, secouristes du travail (SST) identifiés"},
    {"id": "3.2.19", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Équipements de Protection Individuelle (EPI)", "g": "EPI adaptés fournis, port effectif vérifié et sensibilisation du personnel"},
    {"id": "3.2.20", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Sécurité des Rayonnements Ionisants", "g": "Repérage des sources et coordination avec le PCR (Conseiller en Radioprotection)"},
    {"id": "3.2.21", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Sécurité Ferroviaire sur Site", "g": "Respect des gabarits, consignation des voies et signalisation spécifique"},
    {"id": "3.2.22", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Valorisation des Comportements Sûrs", "g": "Programme de reconnaissance encourageant les bonnes pratiques sécurité"},
    {"id": "3.2.23", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Protection Respiratoire", "g": "Choix des masques adaptés, tests d'ajustement (fit-test) et règles de port"},
    {"id": "3.2.24", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Signalisation et Balisage des Dangers", "g": "Panneaux d'avertissement et barrières physiques installés en face du danger"},
    {"id": "3.2.25", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Prévention des Addictions (Alcool / Drogues)", "g": "Politique d'interdiction formalisée et contrôles applicables aux sous-traitants"},
    {"id": "3.2.26", "cat": "3.2 Meilleures Pratiques", "theme": "3. Risques Critiques & Meilleures Pratiques", "q": "Conduite de Chariots et Engins de Chantier", "g": "Autorisations de conduite à jour et vérification des compétences des opérateurs"},
    {"id": "3.2.27", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Outillage Électroportatif", "g": "Outillage conforme, inspecté avant emploi et personnel formé"},
    {"id": "3.2.28", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Risques Biologiques et Pathogènes", "g": "Mesures de prévention contre les risques d'exposition biologique"},
    {"id": "3.2.29", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Gestion des Non-Conformités Sécurité", "g": "Procédure disciplinaire pouvant aller jusqu'à l'exclusion du site en cas de manquement grave"},
    {"id": "3.2.30", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Coactivité près des Zones en Exploitation", "g": "Balisage, isolement des zones de travail et coordination avec l'exploitation"},
    {"id": "3.2.31", "theme": "3. Risques Critiques & Meilleures Pratiques", "cat": "3.2 Meilleures Pratiques", "q": "Outillage à Main Non Motorisé", "g": "Choix d'outils sécurisés (ex: cutters rétractables) et état général contrôlé"},

    # Thème 4 : Planification & Opérations
    {"id": "4.1", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Utilisation d'outils d'analyse des risques au poste", "g": "• Analyses de tâches (AST / JSA), évaluations préalables (PPSA) et causeries quotidiennes"},
    {"id": "4.2", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Visites d'Observation Sécurité (VOS / BOS)", "g": "• Réalisation de visites d'observation à tous les niveaux et suivi des actions associées"},
    {"id": "4.3", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Gestion de la Fatigue et des Heures Supplémentaires", "g": "• Planification du temps de travail conforme et gestion de l'aptitude au poste"},
    {"id": "4.4", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Contrôles Réguliers des Équipements", "g": "• Suivi des contrôles périodiques (engins, nacelles, extincteurs, harnais, outillage)"},
    {"id": "4.5", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Rondes et Visites de Chantier par le Management", "g": "• Contrôles réguliers axés sur le rangement, les accès, l'éclairage et la coactivité"},
    {"id": "4.6", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Réunions et Échanges Sécurité", "g": "• Réunions sécurité quotidiennes/hebdomadaires, quarts d'heure sécurité et revues d'incidents"},
    {"id": "4.7", "theme": "4. Planification & Opérations", "cat": "4. Planification & Opérations", "q": "Encadrement HSE du Chantier", "g": "• Dimensionnement adapté des responsables et préventeurs sécurité sur le terrain"},

    # Thème 5 : Formations & Habilitations Sécurité
    {"id": "5.1", "theme": "5. Formations & Habilitations Sécurité", "cat": "5. Formations & Habilitations Sécurité", "q": "Accueil Sécurité Spécifique au Site", "g": "• Accueil complet couvrant les risques du site, les consignes d'urgence et validation des acquis"},
    {"id": "5.2", "theme": "5. Formations & Habilitations Sécurité", "cat": "5. Formations & Habilitations Sécurité", "q": "Registres des Formations et Habilitations du Personnel", "g": "• Registre à jour : SST, CACES, habilitations électriques, travaux en hauteur, etc."},
    {"id": "5.3", "theme": "5. Formations & Habilitations Sécurité", "cat": "5. Formations & Habilitations Sécurité", "q": "Causeries et Quarts d'Heure Sécurité Hebdomadaires", "g": "• Organisation régulière de réunions d'information et d'échanges sécurité avec les équipes"},
    {"id": "5.4", "theme": "5. Formations & Habilitations Sécurité", "cat": "5. Formations & Habilitations Sécurité", "q": "Formation des Nouveaux Arrivants et des Encadrants", "g": "• Formations à la réalisation des visites d'observation et compétences requises"},
    {"id": "5.5", "theme": "5. Formations & Habilitations Sécurité", "cat": "5. Formations & Habilitations Sécurité", "q": "Suivi des Recyclages de Formation", "g": "• Système d'alerte pour le renouvellement à jour des habilitations et recyclages"}
]

THEME_LIST = [
    "1. Attentes & Engagement",
    "2. Vision & Suivi de la Performance",
    "3. Risques Critiques & Meilleures Pratiques",
    "4. Planification & Opérations",
    "5. Formations & Habilitations Sécurité"
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
    except Exception:
        return f"Fichier joint : {uploaded_file.name}"

def get_color_badge(percentage):
    if percentage >= 80:
        return f"🟢 **{percentage:.1f}% (Conforme / Excellent)**"
    elif percentage >= 50:
        return f"🟠 **{percentage:.1f}% (À améliorer)**"
    else:
        return f"🔴 **{percentage:.1f}% (Non conforme / Risque élevé)**"

# ==========================================
# CALCUL DYNAMIQUE DU SCORE EN TEMPS RÉEL (POUR SIDEBAR ET FORMULAIRE)
# ==========================================
total_q = len(QUESTIONS_DATA)
answered_q_count = 0
total_oui = 0
total_non = 0
total_na = 0

theme_stats = {t: {"oui": 0, "non": 0, "na": 0, "answered": 0, "total": 0} for t in THEME_LIST}

for q in QUESTIONS_DATA:
    theme_stats[q["theme"]]["total"] += 1
    q_key = f"status_{q['id']}"
    if q_key in st.session_state and st.session_state[q_key] is not None:
        answered_q_count += 1
        val = st.session_state[q_key]
        theme_stats[q["theme"]]["answered"] += 1
        if val == "Oui":
            total_oui += 1
            theme_stats[q["theme"]]["oui"] += 1
        elif val == "Non":
            total_non += 1
            theme_stats[q["theme"]]["non"] += 1
        elif val == "N/A":
            total_na += 1
            theme_stats[q["theme"]]["na"] += 1

total_applicable = total_oui + total_non
global_score_pct = (total_oui / total_applicable * 100.0) if total_applicable > 0 else 0.0

# ==========================================
# PANNEAU LATÉRAL (SIDEBAR) - TOUJOURS VISIBLE
# ==========================================
st.sidebar.title("📊 Tableau de Bord HSE")

st.sidebar.markdown("### 🏆 Score Global en Direct")
st.sidebar.metric("Conformité Globale", f"{global_score_pct:.1f} %")
st.sidebar.progress(global_score_pct / 100.0)
st.sidebar.markdown(f"**Statut :** {get_color_badge(global_score_pct)}")

progress_ratio = answered_q_count / total_q
st.sidebar.markdown(f"**Remplissage :** {answered_q_count} / {total_q} questions ({int(progress_ratio*100)}%)")
st.sidebar.progress(progress_ratio)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Navigation & Scores par Thème")

# Affichage des scores individuels par thème dans la sidebar
for idx, t_name in enumerate(THEME_LIST):
    ts = theme_stats[t_name]
    t_app = ts["oui"] + ts["non"]
    t_score = (ts["oui"] / t_app * 100.0) if t_app > 0 else 0.0
    
    status_icon = "🟢" if t_score >= 80 else ("🟠" if t_score >= 50 else "🔴")
    st.sidebar.markdown(f"**{status_icon} Thème {idx+1} : {t_score:.0f}%**")
    st.sidebar.caption(f"*{t_name.split('. ')[1]}* — ({ts['answered']}/{ts['total']} questions renseignées)")

selected_theme_nav = st.sidebar.radio(
    "🎯 Afficher un thème spécifique :",
    options=["📋 Tous les thèmes"] + THEME_LIST,
    key="nav_theme_selection"
)

# Navigation principale par onglets
tab_form, tab_admin = st.tabs(["📝 Formulaire Prestataire", "🔒 Espace Administrateur HSE"])

# ==========================================
# ONGLET 1 : FORMULAIRE PRESTATAIRE
# ==========================================
with tab_form:
    st.markdown("""<div class="main-header">🛡️ Formulaire d'Audit Sécurité & HSE</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="sub-header">Évaluation de conformité pour les entreprises extérieures. Merci de répondre à chaque question et de fournir obligatoirement une justification.</div>""", unsafe_allow_html=True)

    # Bannière récapitulative fixe en haut du formulaire
    col_sc1, col_sc2, col_sc3 = st.columns([1, 1, 2])
    with col_sc1:
        st.metric("Score Global Oui", f"{global_score_pct:.1f} %")
    with col_sc2:
        st.metric("Questions renseignées", f"{answered_q_count} / {total_q}")
    with col_sc3:
        st.markdown(f"**Évaluation du score :** {get_color_badge(global_score_pct)}")
        st.progress(global_score_pct / 100.0)

    with st.expander("📂 Reprendre un brouillon enregistré auparavant (Optionnel)", expanded=False):
        uploaded_draft = st.file_uploader("Importez votre fichier de brouillon (.json) :", type=["json"], key="draft_importer")
        draft_data = {}
        if uploaded_draft is not None:
            try:
                draft_data = json.load(uploaded_draft)
                st.success("✅ Brouillon chargé avec succès ! Vos réponses précédentes ont été appliquées.")
            except Exception:
                st.error("⚠️ Fichier de brouillon invalide.")

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

    # Filtrage selon le thème sélectionné dans la sidebar
    if selected_theme_nav == "📋 Tous les thèmes":
        filtered_themes = THEME_LIST
    else:
        filtered_themes = [selected_theme_nav]

    responses = {}
    uploaded_files_dict = {}

    for t_name in filtered_themes:
        st.markdown(f"## 📌 {t_name}")
        
        # Récupération de l'ensemble des questions du thème
        theme_questions = [q for q in QUESTIONS_DATA if q["theme"] == t_name]
        
        for q in theme_questions:
            # Container visuel distinct pour chaque question avec carte encadrée et titre plus gros
            st.markdown(
                f'<div class="question-card"><div class="question-title-big">[{q["id"]}] {q["q"]}</div></div>',
                unsafe_allow_html=True
            )
            
            if q["g"]:
                st.markdown(f'<div class="guidance-box"><b>Attentes & Guidance :</b><br>{q["g"]}</div>', unsafe_allow_html=True)
            
            saved_status = draft_data.get(f"{q['id']}_Réponse", None)
            saved_justif = draft_data.get(f"{q['id']}_Justification", "")

            c1, c2 = st.columns([1, 2])
            with c1:
                # index=None -> Aucune case cochée par défaut
                status_index = ["Oui", "Non", "N/A"].index(saved_status) if saved_status in ["Oui", "Non", "N/A"] else None
                status = st.radio(
                    f"Réponse pour [{q['id']}]",
                    options=["Oui", "Non", "N/A"],
                    index=status_index,
                    horizontal=True,
                    key=f"status_{q['id']}"
                )
            with c2:
                justification = st.text_area(
                    f"Justification obligatoire pour [{q['id']}] *",
                    value=saved_justif,
                    placeholder="Justification OBLIGATOIRE (procédure interne, preuve, précision ou plan d'action)...",
                    key=f"justif_{q['id']}",
                    height=90
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
                
            st.markdown("<hr style='margin: 20px 0; border-top: 2px dashed #94A3B8;'>", unsafe_allow_html=True)

    # Consolidation de toutes les réponses (y compris des thèmes non affichés actuellement)
    for q in QUESTIONS_DATA:
        if q['id'] not in responses:
            q_stat = st.session_state.get(f"status_{q['id']}", None)
            q_just = st.session_state.get(f"justif_{q['id']}", "")
            responses[q['id']] = {
                "status": q_stat,
                "justification": q_just
            }

    submit_button = st.button("🚀 VALIDER ET ENVOYER L'AUDIT")

    if submit_button:
        missing_fields = []
        if not company_name: missing_fields.append("Nom de l'entreprise")
        if not auditor_name: missing_fields.append("Nom du déclarant")
        if not site_location: missing_fields.append("Site / Chantier")
        
        unanswered = [q_id for q_id, res in responses.items() if res["status"] is None]
        # Justification OBLIGATOIRE peu importe la réponse cochée (Oui, Non ou N/A)
        unjustified = [q_id for q_id, res in responses.items() if res["status"] is not None and not res["justification"].strip()]
                
        if missing_fields:
            st.error(f"⚠️ Veuillez remplir les informations obligatoires : {', '.join(missing_fields)}.")
        elif unanswered:
            st.warning(f"⚠️ Vous devez répondre à toutes les questions (54 au total). Question(s) non renseignée(s) : {', '.join(unanswered)}")
        elif unjustified:
            st.warning(f"⚠️ La justification est OBLIGATOIRE pour chaque question (même pour les réponses 'Oui'). Question(s) sans justification : {', '.join(unjustified)}")
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
    st.subheader("💾 Sauvegarder votre avancement")
    draft_export = {
        "Entreprise": company_name if 'company_name' in locals() else "",
        "Déclarant": auditor_name if 'auditor_name' in locals() else "",
        "Site": site_location if 'site_location' in locals() else "",
    }
    if 'responses' in locals():
        for q_id, res in responses.items():
            draft_export[f"{q_id}_Réponse"] = res["status"] if res["status"] is not None else ""
            draft_export[f"{q_id}_Justification"] = res["justification"]

    st.download_button(
        label="💾 Télécharger le fichier de brouillon (.json)",
        data=json.dumps(draft_export, ensure_ascii=False, indent=2),
        file_name=f"Brouillon_Audit_{company_name if 'company_name' in locals() and company_name else 'Incomplet'}.json",
        mime="application/json"
    )

# ==========================================
# ONGLET 2 : ESPACE ADMINISTRATEUR HSE (PROTÉGÉ PAR MOT DE PASSE)
# ==========================================
with tab_admin:
    st.markdown("""<div class="main-header">🔒 Espace d'Administration HSE</div>""", unsafe_allow_html=True)
    
    ADMIN_PASSWORD = st.secrets.get("admin_password", "HSE2026Securite!")
    input_pwd = st.text_input("🔑 Saisissez le mot de passe Administrateur :", type="password")
    
    if input_pwd == "":
        st.info("🔒 Cet espace est strictement réservé à la consultation administrateur.")
    elif input_pwd != ADMIN_PASSWORD:
        st.error("❌ Mot de passe incorrect.")
    else:
        st.success("🔓 Accès administrateur autorisé.")
        st.markdown("""<div class="sub-header">Consultez l'ensemble des audits validés, analysez le score global et visualisez le score par thème.</div>""", unsafe_allow_html=True)
        
        if st.button("🔄 Actualiser la liste des audits"):
            st.cache_data.clear()

        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_audits = conn.read()
            df_audits = df_audits.dropna(how="all")
        except Exception:
            df_audits = pd.DataFrame()

        if df_audits.empty:
            st.info("Aucun audit n'a encore été enregistré dans la base.")
        else:
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
            st.subheader(f"📄 Fiche Audit : {selected_row.get('Entreprise', 'N/A')}")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🏢 Entreprise", str(selected_row.get("Entreprise", "N/A")))
            c2.metric("👤 Déclarant", str(selected_row.get("Déclarant", "N/A")))
            c3.metric("📍 Site", str(selected_row.get("Site", "N/A")))
            c4.metric("📅 Date", str(selected_row.get("Date", "N/A")))
            
            # Calcul des totaux et du score global
            oui_count = sum(1 for col in selected_row.index if col.endswith("_Réponse") and str(selected_row[col]).strip() == "Oui")
            non_count = sum(1 for col in selected_row.index if col.endswith("_Réponse") and str(selected_row[col]).strip() == "Non")
            na_count = sum(1 for col in selected_row.index if col.endswith("_Réponse") and str(selected_row[col]).strip() == "N/A")
            
            total_applicable_admin = oui_count + non_count
            score_percentage_admin = (oui_count / total_applicable_admin * 100) if total_applicable_admin > 0 else 0.0
            
            st.markdown("### 📊 Score Total & Conformité Globale")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Score Global Oui (%)", f"{score_percentage_admin:.1f} %")
            m2.metric("✅ Conforme (Oui)", oui_count)
            m3.metric("❌ Non Conforme (Non)", non_count)
            m4.metric("⚪ Non Applicable (N/A)", na_count)
            
            # Échelle de couleur visuelle pour le résultat global
            st.markdown(f"**Évaluation du score total :** {get_color_badge(score_percentage_admin)}")
            st.progress(score_percentage_admin / 100.0)
            
            st.markdown("---")
            st.markdown("### 🎯 Score Détaillé par Thème (5 Thèmes Sécurité)")
            
            cols_theme = st.columns(5)
            
            for idx_t, theme_name in enumerate(THEME_LIST):
                theme_questions = [q for q in QUESTIONS_DATA if q["theme"] == theme_name]
                t_oui = 0
                t_non = 0
                t_na = 0
                
                for q in theme_questions:
                    res_val = str(selected_row.get(f"{q['id']}_Réponse", "")).strip()
                    if res_val == "Oui":
                        t_oui += 1
                    elif res_val == "Non":
                        t_non += 1
                    elif res_val == "N/A":
                        t_na += 1
                
                t_appl = t_oui + t_non
                t_score = (t_oui / t_appl * 100) if t_appl > 0 else 0.0
                
                with cols_theme[idx_t]:
                    st.markdown(f"**Thème {idx_t+1}**")
                    st.caption(f"*{theme_name}*")
                    st.metric("Score", f"{t_score:.0f} %", f"{t_oui}/{t_appl} Oui")
                    
                    if t_score >= 80:
                        st.success("🟢 Conforme")
                    elif t_score >= 50:
                        st.warning("🟠 Moyen")
                    else:
                        st.error("🔴 Critique")
                        
                    st.caption(f"Oui: {t_oui} | Non: {t_non} | N/A: {t_na}")
            
            st.markdown("---")
            st.markdown("### 🔍 Détail des Questions par Thème")
            
            for theme_name in THEME_LIST:
                st.markdown(f"#### 📌 {theme_name}")
                theme_q = [q for q in QUESTIONS_DATA if q["theme"] == theme_name]
                
                for q in theme_q:
                    q_id = q["id"]
                    resp_val = str(selected_row.get(f"{q_id}_Réponse", "Non renseigné"))
                    justif_val = str(selected_row.get(f"{q_id}_Justification", "Aucune justification"))
                    file_val = str(selected_row.get(f"{q_id}_Fichier", ""))
                    
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
                            st.markdown(f"📎 **Pièce jointe :** [Ouvrir le document]({file_val})")
                        elif file_val:
                            st.write(f"📎 **Pièce jointe :** {file_val}")
                        else:
                            st.caption("📎 Aucune pièce jointe transmise pour cette question.")
