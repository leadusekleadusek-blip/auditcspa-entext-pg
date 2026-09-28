import customtkinter as ctk
import tkinter as tk
from PIL import Image
import urllib.request
from io import BytesIO
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class PGWorkPermitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("P&G Amiens — Work Permit IT (Mode Kiosk)")
        self.geometry("1220x920")
        self.configure(fg_color="#f8fafc")

        # Palette P&G
        self.PG_BLUE = "#003366"
        self.PG_LIGHT_BLUE = "#0056b3"
        self.PG_BG = "#f8fafc"
        self.PG_CARD = "#ffffff"
        self.PG_GRAY = "#cbd5e1"

        self.logo_image = self.charger_logo_pg()

        self.db_societes = ["ABYLSEN", "APAVE", "AXIMA", "ENGIE", "EULER"]
        self.db_pdps = ["PDP-2026-042 (Bâtiment M1)", "PDP-2026-089 (Bâtiment M2)", "PDP-2026-104 (Logistique)"]
        self.db_n2 = ["Léa DUSEK", "Matthieu MARTIN", "Alexandre LEFEBVRE", "Cindy BERNARD"]

        # MAPPING AUTOMATIQUE : Zone PDP -> Point de Rassemblement & Confinement & Urgences
        self.db_zones_carto = {
            "Bâtiment M1 - Zone Production": {
                "pr": "PR-2 (Parking Ouest)",
                "confinement": "ZC-01 (Hall M1)",
                "urgence": "03.22.54.33.33 (Poste Garde M1)"
            },
            "Bâtiment M1 - Bureaux": {
                "pr": "PR-2 (Parking Ouest)",
                "confinement": "ZC-01 (Hall M1)",
                "urgence": "03.22.54.30.00 (Infirmerie M1)"
            },
            "Bâtiment M2 - Conditionnement": {
                "pr": "PR-4 (Zone Nord)",
                "confinement": "ZC-03 (Atrium M2)",
                "urgence": "03.22.54.33.34 (Poste Garde M2)"
            },
            "Zone Extérieure / Logistique": {
                "pr": "PR-1 (Entrée Principale)",
                "confinement": "ZC-00 (Poste Central)",
                "urgence": "03.22.54.33.33 (SAMU Site)"
            }
        }

        self.etapes_noms = [
            "Entreprise", 
            "PDP", 
            "Responsable N2", 
            "Zone & Urgences", 
            "STA & EPI", 
            "Formulaires Spécifiques", 
            "Intervenants & Signatures"
        ]

        # Structure complète des données
        self.data = {
            "societe": ctk.StringVar(value="ABYLSEN"),
            "pdp": ctk.StringVar(value="PDP-2026-042 (Bâtiment M1)"),
            "n2_nom": ctk.StringVar(value="Léa DUSEK"),
            "lieu_pdp": ctk.StringVar(value="Bâtiment M1 - Bureaux"),
            "lieu_precision": ctk.StringVar(value="1er étage, Bureau 104"),
            "description": ctk.StringVar(value="Peinture acrylique mur nord bureau 104"),
            
            # Auto-remplis selon la zone
            "pr_auto": ctk.StringVar(value="PR-2 (Parking Ouest)"),
            "confinement_auto": ctk.StringVar(value="ZC-01 (Hall M1)"),
            "urgence_auto": ctk.StringVar(value="03.22.54.30.00 (Infirmerie M1)"),

            # Liste dynamique des co-intervenants
            "intervenants": ["Léa DUSEK"],

            # --- STA COMPLÈTE ---
            "sta": {
                "espace_exigu": ctk.BooleanVar(value=True),
                "bruit_80db": ctk.BooleanVar(value=False),
                "travail_hauteur": ctk.BooleanVar(value=False),
                "escalier_tremie": ctk.BooleanVar(value=True),
                "fds_presente": ctk.BooleanVar(value=True),
                "ventilation_ok": ctk.BooleanVar(value=True),
                "sol_glissant": ctk.BooleanVar(value=False),
                "outillage_electro": ctk.BooleanVar(value=True)
            },

            # --- EPI COMPLETS ---
            "epi": {
                "chaussures": ctk.BooleanVar(value=True),
                "casque_jugulaire": ctk.BooleanVar(value=True),
                "lunettes_en166": ctk.BooleanVar(value=True),
                "gants_coupure": ctk.BooleanVar(value=True),
                "gilet_visibilite": ctk.BooleanVar(value=True),
                "masque_ffp2": ctk.BooleanVar(value=True),
                "harnais_anti_chute": ctk.BooleanVar(value=False),
                "bouchons_casque": ctk.BooleanVar(value=False)
            },

            # --- DÉCLENCHEURS PERMIS SPÉCIFIQUES & DÉROGATIONS ---
            "risques_specifiques": {
                "points_chauds": ctk.BooleanVar(value=False),
                "espace_confine": ctk.BooleanVar(value=False),
                "consignation_loto": ctk.BooleanVar(value=False),
                "grutage_levage": ctk.BooleanVar(value=False),
                "systeme_risque": ctk.BooleanVar(value=False)
            },
            "derogations": {
                "meuleuse_angle": ctk.BooleanVar(value=False),
                "cutter_lame_ouverte": ctk.BooleanVar(value=False),
                "echelle_escabeau": ctk.BooleanVar(value=False)
            },

            # --- CONTENUS EXHAUSTIFS PERMIS SPÉCIFIQUES ---
            "details_espace_confine": {
                "mesure_o2": ctk.StringVar(value="20.9 %"),
                "mesure_h2s": ctk.StringVar(value="0 ppm"),
                "mesure_co": ctk.StringVar(value="0 ppm"),
                "nom_vigie": ctk.StringVar(value=""),
                "tel_vigie": ctk.StringVar(value=""),
                "ventilation_forcee": ctk.BooleanVar(value=True),
                "harnais_tripode": ctk.BooleanVar(value=True)
            },
            "details_points_chauds": {
                "nature_travaux": ctk.StringVar(value="Soudure Chalumeau / Meulage"),
                "permis_valide_30min": ctk.BooleanVar(value=True),
                "nettoyage_rayon_10m": ctk.BooleanVar(value=True),
                "extincteur_eau_poudre": ctk.BooleanVar(value=True),
                "ronde_securite_2h": ctk.BooleanVar(value=True)
            },
            "details_consignation": {
                "fluide_electrique": ctk.BooleanVar(value=True),
                "fluide_vapeur": ctk.BooleanVar(value=False),
                "numero_cadenas": ctk.StringVar(value="LOTO-PG-884"),
                "nom_charge_consignation": ctk.StringVar(value="")
            },
            "details_derogation": {
                "motif_absence_alternative": ctk.StringVar(value="Découpe en angle exigu"),
                "accord_casque_rouge": ctk.StringVar(value="EHS-AMIENS-VALIDED")
            }
        }

        self.setup_header()
        
        self.main_container = ctk.CTkFrame(self, fg_color=self.PG_BG, corner_radius=0)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=5)

        self.setup_stepper_bar()
        self.afficher_accueil()

    def charger_logo_pg(self):
        try:
            url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Procter_%26_Gamble_logo.svg/1024px-Procter_%26_Gamble_logo.svg.png"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            raw_data = urllib.request.urlopen(req).read()
            img = Image.open(BytesIO(raw_data))
            return ctk.CTkImage(light_image=img, dark_image=img, size=(90, 90))
        except Exception:
            return None

    def setup_header(self):
        header = ctk.CTkFrame(self, fg_color=self.PG_BLUE, height=65, corner_radius=0)
        header.pack(fill="x", side="top")

        lbl_title = ctk.CTkLabel(
            header, text="PROCTER & GAMBLE — AMIENS", 
            font=ctk.CTkFont(family="Inter", size=17, weight="bold"), text_color="white"
        )
        lbl_title.pack(side="left", padx=20, pady=12)

        lbl_subtitle = ctk.CTkLabel(
            header, text="WORK PERMIT IT  |  BORNE TACTILE KIOSK", 
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#93c5fd"
        )
        lbl_subtitle.pack(side="right", padx=20, pady=12)

    def setup_stepper_bar(self):
        self.footer = ctk.CTkFrame(self, fg_color="#ffffff", height=85, corner_radius=0, border_width=1, border_color="#e2e8f0")
        self.footer.pack(fill="x", side="bottom")

        self.canvas_stepper = tk.Canvas(self.footer, height=70, bg="#ffffff", highlightthickness=0)
        self.canvas_stepper.pack(fill="x", expand=True, padx=30, pady=5)

    def dessiner_stepper(self, etape_active):
        self.canvas_stepper.delete("all")
        self.canvas_stepper.update()
        
        w = self.canvas_stepper.winfo_width()
        if w < 100:
            w = 1000

        n = len(self.etapes_noms)
        padding = 60
        step_width = (w - 2 * padding) / (n - 1)
        y = 25
        r = 15

        if etape_active == 0:
            self.canvas_stepper.create_line(padding, y, w - padding, y, fill=self.PG_GRAY, width=3)
            for i in range(n):
                cx = padding + i * step_width
                self.canvas_stepper.create_oval(cx - r, y - r, cx + r, y + r, fill="#ffffff", outline=self.PG_GRAY, width=2)
                self.canvas_stepper.create_text(cx, y, text=str(i + 1), fill=self.PG_GRAY, font=("Inter", 10, "bold"))
                self.canvas_stepper.create_text(cx, y + 25, text=self.etapes_noms[i], fill=self.PG_GRAY, font=("Inter", 8))
            return

        self.canvas_stepper.create_line(padding, y, w - padding, y, fill=self.PG_GRAY, width=3)
        active_line_end = padding + (etape_active - 1) * step_width
        if active_line_end > padding:
            self.canvas_stepper.create_line(padding, y, active_line_end, y, fill=self.PG_BLUE, width=3)

        for i in range(n):
            cx = padding + i * step_width
            num = i + 1

            if num <= etape_active:
                self.canvas_stepper.create_oval(cx - r, y - r, cx + r, y + r, fill="#ffffff", outline=self.PG_BLUE, width=3)
                self.canvas_stepper.create_text(cx, y, text=str(num), fill=self.PG_BLUE, font=("Inter", 10, "bold"))
                self.canvas_stepper.create_text(cx, y + 25, text=self.etapes_noms[i], fill=self.PG_BLUE, font=("Inter", 8, "bold"))
            else:
                self.canvas_stepper.create_oval(cx - r, y - r, cx + r, y + r, fill="#ffffff", outline=self.PG_GRAY, width=2)
                self.canvas_stepper.create_text(cx, y, text=str(num), fill=self.PG_GRAY, font=("Inter", 10, "bold"))
                self.canvas_stepper.create_text(cx, y + 25, text=self.etapes_noms[i], fill="#94a3b8", font=("Inter", 8))

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def render_navigation(self, fn_prev, fn_next):
        f_nav = ctk.CTkFrame(self.main_container, fg_color="transparent")
        f_nav.pack(fill="x", pady=10, padx=10)

        if fn_prev:
            btn_p = ctk.CTkButton(f_nav, text="⬅ Précédent", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#64748b", hover_color="#475569", height=40, command=fn_prev)
            btn_p.pack(side="left")

        if fn_next:
            btn_n = ctk.CTkButton(f_nav, text="Suivant ➔", font=ctk.CTkFont(size=12, weight="bold"), fg_color=self.PG_BLUE, hover_color=self.PG_LIGHT_BLUE, height=40, command=fn_next)
            btn_n.pack(side="right")

    # --- ACCUEIL ---
    def afficher_accueil(self):
        self.clear_container()
        self.dessiner_stepper(0)

        card = ctk.CTkFrame(self.main_container, fg_color=self.PG_CARD, corner_radius=16, border_width=1, border_color="#e2e8f0")
        card.pack(expand=True, padx=40, pady=20, fill="both")

        if self.logo_image:
            lbl_logo = ctk.CTkLabel(card, image=self.logo_image, text="")
            lbl_logo.pack(pady=(20, 5))

        lbl_welcome = ctk.CTkLabel(card, text="Gestion des Permis de Travail (PT)", font=ctk.CTkFont(family="Inter", size=22, weight="bold"), text_color=self.PG_BLUE)
        lbl_welcome.pack(pady=(5, 5))

        lbl_sub = ctk.CTkLabel(card, text="Saisie rapide & propagation automatique sur la borne tactile.", font=ctk.CTkFont(family="Inter", size=13), text_color="#64748b")
        lbl_sub.pack(pady=(0, 20))

        btn_start = ctk.CTkButton(
            card, text="🚀  COMMANCER MON PERMIS DE TRAVAIL", 
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            fg_color=self.PG_BLUE, hover_color=self.PG_LIGHT_BLUE,
            height=50, corner_radius=10, command=self.ecran_1_societe
        )
        btn_start.pack(pady=10, ipadx=20)

    # --- ÉCRAN 1 : SOCIÉTÉ ---
    def ecran_1_societe(self):
        self.clear_container()
        self.dessiner_stepper(1)
        card = ctk.CTkFrame(self.main_container, fg_color=self.PG_CARD, corner_radius=12, border_width=1, border_color="#e2e8f0")
        card.pack(fill="x", pady=20, padx=20, ipady=15)
        ctk.CTkLabel(card, text="1. Entreprise Extérieure (EE)", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=20, pady=10)
        combo = ctk.CTkOptionMenu(card, variable=self.data["societe"], values=self.db_societes, font=ctk.CTkFont(size=13), height=40, fg_color=self.PG_BLUE, button_color=self.PG_LIGHT_BLUE)
        combo.pack(anchor="w", padx=20, pady=10)
        self.render_navigation(self.afficher_accueil, self.ecran_2_pdp)

    # --- ÉCRAN 2 : PDP ---
    def ecran_2_pdp(self):
        self.clear_container()
        self.dessiner_stepper(2)
        card = ctk.CTkFrame(self.main_container, fg_color=self.PG_CARD, corner_radius=12, border_width=1, border_color="#e2e8f0")
        card.pack(fill="x", pady=20, padx=20, ipady=15)
        ctk.CTkLabel(card, text=f"2. Plan de Prévention (PDP) — {self.data['societe'].get()}", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=20, pady=10)
        combo = ctk.CTkOptionMenu(card, variable=self.data["pdp"], values=self.db_pdps, font=ctk.CTkFont(size=13), width=350, height=40, fg_color=self.PG_BLUE, button_color=self.PG_LIGHT_BLUE)
        combo.pack(anchor="w", padx=20, pady=10)
        self.render_navigation(self.ecran_1_societe, self.ecran_3_n2)

    # --- ÉCRAN 3 : RESPONSABLE N2 ---
    def ecran_3_n2(self):
        self.clear_container()
        self.dessiner_stepper(3)
        card = ctk.CTkFrame(self.main_container, fg_color=self.PG_CARD, corner_radius=12, border_width=1, border_color="#e2e8f0")
        card.pack(fill="x", pady=20, padx=20, ipady=15)
        ctk.CTkLabel(card, text="3. Responsable N2 Présent sur le Chantier", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=20, pady=10)
        combo = ctk.CTkOptionMenu(card, variable=self.data["n2_nom"], values=self.db_n2, font=ctk.CTkFont(size=13), width=300, height=40, fg_color=self.PG_BLUE, button_color=self.PG_LIGHT_BLUE)
        combo.pack(anchor="w", padx=20, pady=10)
        self.render_navigation(self.ecran_2_pdp, self.ecran_4_lieu_urgences)

    # --- ÉCRAN 4 : CARTOGRAPHIE ZONE PDP -> AUTO CONFINEMENT & PR ---
    def ecran_4_lieu_urgences(self):
        self.clear_container()
        self.dessiner_stepper(4)

        card = ctk.CTkFrame(self.main_container, fg_color=self.PG_CARD, corner_radius=12, border_width=1, border_color="#e2e8f0")
        card.pack(fill="x", pady=10, padx=20, ipady=10)

        ctk.CTkLabel(card, text="4. Localisation & Assignation Automatique des Urgences", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=20, pady=(10, 5))

        # Choix de la zone PDP avec maj automatique
        ctk.CTkLabel(card, text="Sélectionnez la Zone du PDP :", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(5,0))
        
        def on_zone_change(choice):
            m = self.db_zones_carto.get(choice, {})
            self.data["pr_auto"].set(m.get("pr", "PR-Standard"))
            self.data["confinement_auto"].set(m.get("confinement", "ZC-Standard"))
            self.data["urgence_auto"].set(m.get("urgence", "03.22.54.33.33"))

        combo_lieu = ctk.CTkOptionMenu(card, variable=self.data["lieu_pdp"], values=list(self.db_zones_carto.keys()), command=on_zone_change, width=360, height=35)
        combo_lieu.pack(anchor="w", padx=20, pady=5)

        ctk.CTkLabel(card, text="Précision d'emplacement (Local, Bureau, Ligne) :", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(10,0))
        entry_prec = ctk.CTkEntry(card, textvariable=self.data["lieu_precision"], width=400, height=35)
        entry_prec.pack(anchor="w", padx=20, pady=5)

        ctk.CTkLabel(card, text="Description détaillée de la tâche :", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(10,0))
        entry_desc = ctk.CTkEntry(card, textvariable=self.data["description"], width=500, height=35)
        entry_desc.pack(anchor="w", padx=20, pady=5)

        # BOX AFFICHAGE CONFINEMENT ET PR AUTOMATIQUE
        card_auto = ctk.CTkFrame(card, fg_color="#fffbebfb", border_width=1, border_color="#fef3c7", corner_radius=8)
        card_auto.pack(fill="x", padx=20, pady=15, ipady=5)

        ctk.CTkLabel(card_auto, text="📍 Assignation Sécurité Secteur (Automatique)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#b45309").pack(anchor="w", padx=15, pady=5)
        
        f_info = ctk.CTkFrame(card_auto, fg_color="transparent")
        f_info.pack(fill="x", padx=15, pady=2)
        
        ctk.CTkLabel(f_info, text="Point de Rassemblement :", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(f_info, textvariable=self.data["pr_auto"], font=ctk.CTkFont(size=11), text_color=self.PG_BLUE).grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(f_info, text="Zone de Confinement :", font=ctk.CTkFont(size=11, weight="bold")).grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(f_info, textvariable=self.data["confinement_auto"], font=ctk.CTkFont(size=11), text_color=self.PG_BLUE).grid(row=1, column=1, sticky="w", padx=10)

        ctk.CTkLabel(f_info, text="Poste Urgence :", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w")
        ctk.CTkLabel(f_info, textvariable=self.data["urgence_auto"], font=ctk.CTkFont(size=11), text_color="#b91c1c").grid(row=2, column=1, sticky="w", padx=10)

        self.render_navigation(self.ecran_3_n2, self.ecran_5_sta)

    # --- ÉCRAN 5 : STA / EPI / RISQUES ---
    def ecran_5_sta(self):
        self.clear_container()
        self.dessiner_stepper(5)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color=self.PG_BG, height=480)
        scroll.pack(fill="both", expand=True)

        card_env = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=10, border_width=1, border_color="#e2e8f0")
        card_env.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(card_env, text="1. STA — Risques Environnementaux", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=12, pady=4)
        f_env = ctk.CTkFrame(card_env, fg_color="transparent")
        f_env.pack(fill="x", padx=12, pady=4)
        ctk.CTkCheckBox(f_env, text="Espace exigu", variable=self.data["sta"]["espace_exigu"]).grid(row=0, column=0, padx=8, pady=3, sticky="w")
        ctk.CTkCheckBox(f_env, text="Bruit > 80 dB", variable=self.data["sta"]["bruit_80db"]).grid(row=0, column=1, padx=8, pady=3, sticky="w")
        ctk.CTkCheckBox(f_env, text="Proximité escalier", variable=self.data["sta"]["escalier_tremie"]).grid(row=0, column=2, padx=8, pady=3, sticky="w")

        card_epi = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=10, border_width=1, border_color="#e2e8f0")
        card_epi.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(card_epi, text="2. Équipements de Protection Individuelle (EPI)", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=12, pady=4)
        f_epi = ctk.CTkFrame(card_epi, fg_color="transparent")
        f_epi.pack(fill="x", padx=12, pady=4)
        ctk.CTkCheckBox(f_epi, text="Chaussures montantes", variable=self.data["epi"]["chaussures"]).grid(row=0, column=0, padx=8, pady=3, sticky="w")
        ctk.CTkCheckBox(f_epi, text="Casque + Jugulaire", variable=self.data["epi"]["casque_jugulaire"]).grid(row=0, column=1, padx=8, pady=3, sticky="w")
        ctk.CTkCheckBox(f_epi, text="Masque FFP2", variable=self.data["epi"]["masque_ffp2"]).grid(row=0, column=2, padx=8, pady=3, sticky="w")

        card_spe = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=10, border_width=1, border_color="#fca5a5")
        card_spe.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(card_spe, text="3. Sélection des Permis Spécifiques (HRT) & Dérogations", font=ctk.CTkFont(size=13, weight="bold"), text_color="#b91c1c").pack(anchor="w", padx=12, pady=4)
        
        f_spe = ctk.CTkFrame(card_spe, fg_color="transparent")
        f_spe.pack(fill="x", padx=12, pady=4)
        ctk.CTkCheckBox(f_spe, text="Points Chauds / Soudure", variable=self.data["risques_specifiques"]["points_chauds"]).grid(row=0, column=0, padx=8, pady=5, sticky="w")
        ctk.CTkCheckBox(f_spe, text="Espace Confiné", variable=self.data["risques_specifiques"]["espace_confine"]).grid(row=0, column=1, padx=8, pady=5, sticky="w")
        ctk.CTkCheckBox(f_spe, text="Consignation (LOTO)", variable=self.data["risques_specifiques"]["consignation_loto"]).grid(row=0, column=2, padx=8, pady=5, sticky="w")
        ctk.CTkCheckBox(f_spe, text="Dérogation Meuleuse", variable=self.data["derogations"]["meuleuse_angle"], text_color="#b91c1c").grid(row=1, column=0, padx=8, pady=5, sticky="w")

        self.render_navigation(self.ecran_4_lieu_urgences, self.valider_passage_ecran_5)

    def valider_passage_ecran_5(self):
        has_specifique = (
            any(v.get() for v in self.data["risques_specifiques"].values()) or 
            any(v.get() for v in self.data["derogations"].values())
        )
        if has_specifique:
            self.ecran_6_formulaires_specifiques()
        else:
            self.ecran_7_intervenants_signatures()

    # --- ÉCRAN 6 : SAMPLES FORMULAIRES SPÉCIFIQUES ---
    def ecran_6_formulaires_specifiques(self):
        self.clear_container()
        self.dessiner_stepper(6)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color=self.PG_BG, height=480)
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Formulaires Spécifiques & Dérogations Déclenchés", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=10, pady=(5, 10))

        if self.data["risques_specifiques"]["espace_confine"].get():
            card = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=12, border_width=2, border_color=self.PG_BLUE)
            card.pack(fill="x", pady=8, padx=5, ipady=10)
            ctk.CTkLabel(card, text=" 🦺  PERMIS ESPACE CONFINÉ (CBA 105) ", font=ctk.CTkFont(size=13, weight="bold"), text_color="white", fg_color=self.PG_BLUE, corner_radius=6).pack(anchor="w", padx=15, pady=8)
            f_fields = ctk.CTkFrame(card, fg_color="transparent")
            f_fields.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(f_fields, text="Taux O2 mesuré :", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=5, pady=3, sticky="w")
            ctk.CTkEntry(f_fields, textvariable=self.data["details_espace_confine"]["mesure_o2"], width=120).grid(row=0, column=1, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(f_fields, text="Vigie Extérieure :", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, padx=5, pady=3, sticky="w")
            ctk.CTkEntry(f_fields, textvariable=self.data["details_espace_confine"]["nom_vigie"], width=200).grid(row=0, column=3, padx=5, pady=3, sticky="w")

        if self.data["risques_specifiques"]["points_chauds"].get():
            card = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=12, border_width=2, border_color="#d97706")
            card.pack(fill="x", pady=8, padx=5, ipady=10)
            ctk.CTkLabel(card, text=" 🔥  PERMIS POINTS CHAUDS / SOUDURE ", font=ctk.CTkFont(size=13, weight="bold"), text_color="white", fg_color="#d97706", corner_radius=6).pack(anchor="w", padx=15, pady=8)
            f_fields = ctk.CTkFrame(card, fg_color="transparent")
            f_fields.pack(fill="x", padx=15, pady=5)
            ctk.CTkCheckBox(f_fields, text="Vigie 30 min après travaux", variable=self.data["details_points_chauds"]["permis_valide_30min"]).grid(row=0, column=0, padx=5, pady=3, sticky="w")
            ctk.CTkCheckBox(f_fields, text="Extincteur présent sur zone", variable=self.data["details_points_chauds"]["extincteur_eau_poudre"]).grid(row=0, column=1, padx=5, pady=3, sticky="w")

        self.render_navigation(self.ecran_5_sta, self.ecran_7_intervenants_signatures)

    # --- ÉCRAN 7 : GESTION DES INTERVENANTS & SIGNATURES MULTIPLES ---
    def ecran_7_intervenants_signatures(self):
        self.clear_container()
        self.dessiner_stepper(7)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color=self.PG_BG, height=480)
        scroll.pack(fill="both", expand=True)

        card_top = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=12, border_width=1, border_color="#e2e8f0")
        card_top.pack(fill="x", pady=8, padx=5, ipady=5)

        ctk.CTkLabel(card_top, text="Liste des Compagnons / Intervenants Présents", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=15, pady=5)

        # Ajout dynamique d'un intervenant
        f_add = ctk.CTkFrame(card_top, fg_color="transparent")
        f_add.pack(fill="x", padx=15, pady=5)

        entry_new_name = ctk.CTkEntry(f_add, placeholder_text="Nom Prénom de l'intervenant...", width=250)
        entry_new_name.pack(side="left", padx=(0, 10))

        def ajouter_intervenant():
            nom = entry_new_name.get().strip()
            if nom and nom not in self.data["intervenants"]:
                self.data["intervenants"].append(nom)
                entry_new_name.delete(0, 'end')
                self.ecran_7_intervenants_signatures()

        ctk.CTkButton(f_add, text="+ Ajouter l'intervenant", fg_color=self.PG_BLUE, command=ajouter_intervenant).pack(side="left")

        # Affichage des cartes de signature pour le N2 et tous les intervenants
        for idx, nom in enumerate(self.data["intervenants"]):
            card_sig = ctk.CTkFrame(scroll, fg_color=self.PG_CARD, corner_radius=10, border_width=1, border_color="#cbd5e1")
            card_sig.pack(fill="x", pady=5, padx=5, ipady=5)

            role = "RESPONSABLE N2" if idx == 0 else f"INTERVENANT {idx+1}"
            ctk.CTkLabel(card_sig, text=f"✍️ Signature {role} : {nom}", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.PG_BLUE).pack(anchor="w", padx=12, pady=4)

            cv = tk.Canvas(card_sig, width=350, height=50, bg="#f1f5f9", highlightthickness=1, highlightbackground="#cbd5e1")
            cv.pack(anchor="w", padx=12, pady=4)
            cv.create_text(175, 25, text=f"[ Emplacement Signature Tactile : {nom} ]", fill="#64748b", font=("Inter", 9, "italic"))

        btn_submit = ctk.CTkButton(
            self.main_container, 
            text="🚀  SOUMETTRE ET SIGNER LE PERMIS (Batch 7h30)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10b981", hover_color="#059669", height=45, command=self.soumettre
        )
        btn_submit.pack(pady=10)

        has_specifique = (
            any(v.get() for v in self.data["risques_specifiques"].values()) or 
            any(v.get() for v in self.data["derogations"].values())
        )
        fn_prev = self.ecran_6_formulaires_specifiques if has_specifique else self.ecran_5_sta
        self.render_navigation(fn_prev, None)

    def soumettre(self):
        msg = f"Permis de travail soumis pour {self.data['societe'].get()} !\n\n"
        msg += f"• Intervenants signataires : {', '.join(self.data['intervenants'])}\n"
        msg += f"• Point de Rassemblement : {self.data['pr_auto'].get()}\n"
        msg += f"• Zone Confinement : {self.data['confinement_auto'].get()}\n\n"
        msg += "Validation automatique transmise au DO P&G à 07h30."
        messagebox.showinfo("Succès P&G", msg)
        self.afficher_accueil()

if __name__ == "__main__":
    app = PGWorkPermitApp()
    app.mainloop()
