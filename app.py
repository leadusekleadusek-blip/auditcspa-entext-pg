<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit HSE - Inspection Entreprise Extérieure</title>
    <!-- FontAwesome CDN -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- SheetJS (XLSX) CDN -->
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --primary-dark: #1e293b;
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --sidebar-width: 330px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }

        body { background-color: var(--bg-body); color: var(--text-main); display: flex; min-height: 100vh; }

        /* Panneau Latéral (Sidebar Admin) */
        .sidebar {
            width: var(--sidebar-width);
            background-color: var(--primary-dark);
            color: #ffffff;
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0; bottom: 0; left: 0;
            z-index: 100;
            overflow-y: auto;
            box-shadow: 4px 0 10px rgba(0,0,0,0.15);
        }

        .sidebar-header { padding: 20px; background-color: #0f172a; border-bottom: 1px solid #334155; }
        .sidebar-header h2 { font-size: 1.15rem; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 10px; }
        .sidebar-header p { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

        .sidebar-section { padding: 16px 20px; border-bottom: 1px solid #334155; }
        .sidebar-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; margin-bottom: 10px; font-weight: 600; }

        /* Widgets Score */
        .score-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 14px;
            text-align: center;
            margin-bottom: 12px;
        }

        .score-card.recap-card {
            background-color: #0f172a;
            border-color: #3b82f6;
        }

        .score-value { font-size: 2rem; font-weight: 800; color: #38bdf8; line-height: 1; }
        .score-value.recap-value { color: #60a5fa; }
        .score-label { font-size: 0.78rem; color: #cbd5e1; margin-top: 4px; }

        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center; }
        .stat-box { background-color: #0f172a; padding: 6px 4px; border-radius: 6px; }
        .stat-box .num { font-weight: 700; font-size: 1rem; }
        .stat-box.c .num { color: #34d399; }
        .stat-box.nc .num { color: #f87171; }
        .stat-box.na .num { color: #94a3b8; }
        .stat-box .lbl { font-size: 0.65rem; color: #94a3b8; }

        /* Navigation par thèmes */
        .theme-nav { list-style: none; }
        .theme-nav li { margin-bottom: 4px; }
        .theme-nav a { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; color: #cbd5e1; text-decoration: none; border-radius: 6px; font-size: 0.85rem; transition: all 0.2s; }
        .theme-nav a:hover { background-color: #334155; color: #ffffff; }

        .badge-count { background-color: #0f172a; font-size: 0.72rem; padding: 2px 7px; border-radius: 10px; color: #94a3b8; }

        /* Boutons */
        .btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 10px 14px; border: none; border-radius: 6px; font-weight: 600; font-size: 0.88rem; cursor: pointer; transition: background-color 0.2s; margin-bottom: 8px; }
        .btn-excel { background-color: #10b981; color: #ffffff; }
        .btn-excel:hover { background-color: #059669; }
        .btn-archive { background-color: #3b82f6; color: #ffffff; }
        .btn-archive:hover { background-color: #2563eb; }
        .btn-history { background-color: #8b5cf6; color: #ffffff; }
        .btn-history:hover { background-color: #7c3aed; }
        .btn-outline { background-color: transparent; border: 1px solid #475569; color: #cbd5e1; }
        .btn-outline:hover { background-color: #334155; color: #ffffff; }
        .btn-danger { background-color: #ef4444; color: #ffffff; }
        .btn-danger:hover { background-color: #dc2626; }
        .btn-primary { background-color: var(--primary-light); color: white; }

        /* Contenu Principal */
        .main-content { margin-left: var(--sidebar-width); flex: 1; padding: 28px; max-width: 1200px; }

        /* Banner EE */
        .ee-banner { background-color: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); padding: 22px; margin-bottom: 24px; }
        .ee-banner-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 18px; }
        .ee-banner-title { font-size: 1.25rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 10px; }

        .ee-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
        .form-group { display: flex; flex-direction: column; gap: 5px; }
        .form-group label { font-size: 0.82rem; font-weight: 600; color: var(--text-muted); }
        .form-control { padding: 9px 12px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 0.92rem; color: var(--text-main); outline: none; }
        .form-control:focus { border-color: var(--primary-light); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); }

        /* Questions Cards */
        .theme-card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 24px; overflow: hidden; }
        .theme-card-header { background-color: #f1f5f9; padding: 14px 20px; border-bottom: 1px solid var(--border-color); }
        .theme-card-header h3 { font-size: 1.05rem; color: var(--primary-dark); font-weight: 700; }

        .question-item { padding: 18px 20px; border-bottom: 1px solid var(--border-color); }
        .question-item:last-child { border-bottom: none; }
        .question-text { font-size: 0.95rem; font-weight: 600; color: #1e293b; margin-bottom: 10px; }
        .question-num { display: inline-block; background-color: #e2e8f0; color: #475569; font-weight: 700; font-size: 0.78rem; padding: 2px 7px; border-radius: 4px; margin-right: 6px; }

        .response-options { display: flex; gap: 10px; margin-bottom: 10px; }
        .option-label { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 10px; border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600; color: var(--text-muted); transition: all 0.2s; user-select: none; }
        .option-label input[type="radio"] { display: none; }
        .option-label.opt-c:has(input:checked) { background-color: #d1fae5; border-color: #10b981; color: #065f46; }
        .option-label.opt-nc:has(input:checked) { background-color: #fee2e2; border-color: #ef4444; color: #991b1b; }
        .option-label.opt-na:has(input:checked) { background-color: #f1f5f9; border-color: #94a3b8; color: #334155; }

        .justification-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 0.88rem; }

        /* Modales */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1000; align-items: center; justify-content: center; }
        .modal-overlay.active { display: flex; }
        .modal-card { background: #ffffff; border-radius: 12px; width: 100%; max-width: 850px; max-height: 85vh; display: flex; flex-direction: column; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
        .modal-body { overflow-y: auto; flex: 1; padding-right: 4px; }
        .close-btn { background: none; border: none; font-size: 1.3rem; cursor: pointer; color: var(--text-muted); }

        /* Tableau d'historique */
        .history-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
        .history-table th, .history-table td { padding: 10px 12px; border: 1px solid var(--border-color); text-align: left; }
        .history-table th { background-color: #f1f5f9; font-weight: 700; color: var(--primary-dark); }

        .badge-score { display: inline-block; padding: 3px 8px; border-radius: 12px; font-weight: 700; font-size: 0.8rem; }
        .badge-score.good { background-color: #d1fae5; color: #065f46; }
        .badge-score.medium { background-color: #fef3c7; color: #92400e; }
        .badge-score.bad { background-color: #fee2e2; color: #991b1b; }

        .action-btns-cell { display: flex; gap: 6px; }
        .btn-sm { padding: 5px 8px; font-size: 0.78rem; border-radius: 4px; cursor: pointer; border: none; display: inline-flex; align-items: center; gap: 4px; }

        @media (max-width: 900px) {
            body { flex-direction: column; }
            .sidebar { width: 100%; position: relative; height: auto; }
            .main-content { margin-left: 0; }
        }
    </style>
</head>
<body>

    <!-- PANNEAU LATÉRAL (SIDEBAR ADMIN) -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <h2><i class="fa-solid fa-clipboard-check"></i> Audit HSE - EE</h2>
            <p>Gestion & Administration des Audits</p>
        </div>

        <!-- Section Tableau de Bord : Audit en cours -->
        <div class="sidebar-section">
            <div class="sidebar-title">Audit en cours</div>
            <div class="score-card">
                <div class="score-value" id="scorePercent">-%</div>
                <div class="score-label">Taux de Conformité</div>
            </div>
            <div class="stats-grid">
                <div class="stat-box c">
                    <div class="num" id="countC">0</div>
                    <div class="lbl">Conforme</div>
                </div>
                <div class="stat-box nc">
                    <div class="num" id="countNC">0</div>
                    <div class="lbl">Non Conf.</div>
                </div>
                <div class="stat-box na">
                    <div class="num" id="countNA">0</div>
                    <div class="lbl">N/A</div>
                </div>
            </div>
        </div>

        <!-- SECTION RÉCAPITULATIF GÉNÉRAL ADMINISTRATEUR -->
        <div class="sidebar-section">
            <div class="sidebar-title">Récapitulatif Général Administrateur</div>
            <div class="score-card recap-card">
                <div class="score-value recap-value" id="globalAveragePercent">-%</div>
                <div class="score-label">Moyenne Globale des Audits</div>
            </div>
            <div style="font-size: 0.8rem; color: #cbd5e1; text-align: center;">
                Nombre d'audits réalisés : <strong id="totalAuditsCount">0</strong>
            </div>
        </div>

        <!-- Section Navigation par Thème -->
        <div class="sidebar-section" style="flex:1;">
            <div class="sidebar-title">Thèmes de contrôle</div>
            <ul class="theme-nav" id="themeNavList"></ul>
        </div>

        <!-- Section Sauvegarde & Récapitulatifs (Administration) -->
        <div class="sidebar-section">
            <div class="sidebar-title">Gestion & Archives Audits</div>
            
            <button class="btn btn-archive" onclick="saveAndArchiveCurrentAudit()">
                <i class="fa-solid fa-box-archive"></i> Valider & Archiver l'audit
            </button>
            
            <button class="btn btn-history" onclick="openHistoryModal()">
                <i class="fa-solid fa-clock-rotate-left"></i> Anciens Audits (<span id="savedAuditsCount">0</span>)
            </button>

            <button class="btn btn-excel" onclick="exportToExcel()">
                <i class="fa-solid fa-file-excel"></i> Télécharger Excel (.xlsx)
            </button>
            
            <button class="btn btn-outline" onclick="openAddQuestionModal()">
                <i class="fa-solid fa-plus-circle"></i> Ajouter une question
            </button>
            
            <button class="btn btn-outline" onclick="resetForm()">
                <i class="fa-solid fa-rotate-left"></i> Nouvel Audit / Vider
            </button>
        </div>
    </aside>

    <!-- CONTENU PRINCIPAL -->
    <main class="main-content">

        <!-- BANDEAU HAUT : INFORMATIONS ENTREPRISE EXTÉRIEURE -->
        <section class="ee-banner">
            <div class="ee-banner-header">
                <div class="ee-banner-title">
                    <i class="fa-solid fa-building-user"></i> Informations de l'Entreprise Extérieure (EE)
                </div>
                <span style="font-size: 0.82rem; color: var(--text-muted); font-weight: 500;">
                    <i class="fa-solid fa-shield-halved"></i> Audit Sécurité Chantier
                </span>
            </div>

            <div class="ee-grid">
                <div class="form-group">
                    <label for="ee_nom">Raison Sociale / Entreprise Extérieure *</label>
                    <input type="text" id="ee_nom" class="form-control" placeholder="ex: SPIE, VINCI, Bouygues..." onchange="autoSaveDraft()">
                </div>
                <div class="form-group">
                    <label for="ee_intervenant">Nom & Prénom de l'Intervenant EE</label>
                    <input type="text" id="ee_intervenant" class="form-control" placeholder="ex: Marc Dupont" onchange="autoSaveDraft()">
                </div>
                <div class="form-group">
                    <label for="auditeur_nom">Auditeur / Responsable HSE Site *</label>
                    <input type="text" id="auditeur_nom" class="form-control" placeholder="ex: Léa Dusek" onchange="autoSaveDraft()">
                </div>
                <div class="form-group">
                    <label for="audit_date">Date de l'inspection</label>
                    <input type="date" id="audit_date" class="form-control" onchange="autoSaveDraft()">
                </div>
                <div class="form-group">
                    <label for="ee_zone">Chantier / Zone d'intervention *</label>
                    <input type="text" id="ee_zone" class="form-control" placeholder="ex: Bâtiment B - Ligne Conditionnement" onchange="autoSaveDraft()">
                </div>
                <div class="form-group">
                    <label for="ee_pdp">N° Plan de Prévention (PDP) / Permis</label>
                    <input type="text" id="ee_pdp" class="form-control" placeholder="ex: PDP-2026-089" onchange="autoSaveDraft()">
                </div>
            </div>
        </section>

        <!-- CONTENEUR DES QUESTIONNAIRES PAR THÈME -->
        <div id="questionsContainer"></div>

    </main>

    <!-- MODAL 1 : HISTORIQUE ET RÉCAPITULATIF DES ANCIENS AUDITS -->
    <div class="modal-overlay" id="historyModal">
        <div class="modal-card">
            <div class="modal-header">
                <h3><i class="fa-solid fa-clock-rotate-left"></i> Historique des anciens audits enregistrés</h3>
                <button class="close-btn" onclick="closeHistoryModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div style="background-color: #f1f5f9; padding:12px; border-radius:8px; margin-bottom:16px; display:flex; justify-content:space-around; text-align:center;">
                    <div>
                        <div style="font-size:0.75rem; color: var(--text-muted); font-weight:600;">TOTAL AUDITS</div>
                        <div style="font-size:1.3rem; font-weight:700; color: var(--primary-dark);" id="modalTotalAudits">0</div>
                    </div>
                    <div>
                        <div style="font-size:0.75rem; color: var(--text-muted); font-weight:600;">MOYENNE GLOBALE</div>
                        <div style="font-size:1.3rem; font-weight:800; color: #2563eb;" id="modalAvgScore">-%</div>
                    </div>
                </div>

                <table class="history-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Entreprise (EE)</th>
                            <th>Chantier / Zone</th>
                            <th>Auditeur</th>
                            <th>Score</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="historyTableBody"></tbody>
                </table>

                <div style="margin-top:20px; padding-top:15px; border-top:1px solid var(--border-color); display:flex; justify-content:space-between; gap:10px;">
                    <button class="btn btn-outline" style="width:auto; margin:0;" onclick="exportHistoryJSON()">
                        <i class="fa-solid fa-download"></i> Exporter la base (JSON)
                    </button>
                    <button class="btn btn-outline" style="width:auto; margin:0;" onclick="importHistoryJSON()">
                        <i class="fa-solid fa-upload"></i> Importer la base (JSON)
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL 2 : AJOUT DE QUESTION -->
    <div class="modal-overlay" id="addModal">
        <div class="modal-card" style="max-width: 500px;">
            <div class="modal-header">
                <h3>Ajouter une nouvelle question</h3>
                <button class="close-btn" onclick="closeAddQuestionModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group" style="margin-bottom: 12px;">
                    <label for="modal_theme">Thème</label>
                    <select id="modal_theme" class="form-control"></select>
                </div>
                <div class="form-group" style="margin-bottom: 12px;">
                    <label for="modal_qnum">N° Question (ex: Q1.4)</label>
                    <input type="text" id="modal_qnum" class="form-control" placeholder="Q1.4">
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="modal_qtext">Question / Point de contrôle</label>
                    <textarea id="modal_qtext" class="form-control" rows="3" placeholder="Saisir la consigne..."></textarea>
                </div>
                <div style="display:flex; justify-content:flex-end; gap:10px;">
                    <button class="btn btn-outline" style="width:auto;" onclick="closeAddQuestionModal()">Annuler</button>
                    <button class="btn btn-primary" style="width:auto;" onclick="saveNewQuestion()">Ajouter</button>
                </div>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        const defaultAuditStructure = [
            {
                themeId: "theme1",
                themeTitle: "1. Habilitations & Plan de Prévention",
                questions: [
                    { id: "q1_1", num: "Q1.1", text: "Le Plan de Prévention (PDP) est-il signé et disponible sur le chantier ?", response: "", justification: "" },
                    { id: "q1_2", num: "Q1.2", text: "Les intervenants possèdent-ils les habilitations requises (Électrique, CACES, Hauteur) ?", response: "", justification: "" },
                    { id: "q1_3", num: "Q1.3", text: "Le permis de feu / travail spécifique est-il affiché si nécessaire ?", response: "", justification: "" }
                ]
            },
            {
                themeId: "theme2",
                themeTitle: "2. Équipements de Protection Individuelle (EPI)",
                questions: [
                    { id: "q2_1", num: "Q2.1", text: "Port des EPI de base conforme (Casque, Chaussures de sécurité, Gilet haute visibilité) ?", response: "", justification: "" },
                    { id: "q2_2", num: "Q2.2", text: "Port des EPI spécifiques adaptés au risque (Protections auditives, Lunettes, Harnais) ?", response: "", justification: "" }
                ]
            },
            {
                themeId: "theme3",
                themeTitle: "3. Matériel, Outillage & Consignation",
                questions: [
                    { id: "q3_1", num: "Q3.1", text: "Le matériel électroportatif et l'outillage sont-ils en bon état avec contrôle périodique ?", response: "", justification: "" },
                    { id: "q3_2", num: "Q3.2", text: "Les procédures de consignation LOTO (Lockout/Tagout) sont-elles respectées ?", response: "", justification: "" }
                ]
            },
            {
                themeId: "theme4",
                themeTitle: "4. Environnement, Propreté & Déchets",
                questions: [
                    { id: "q4_1", num: "Q4.1", text: "La zone de travail est-elle balisée et l'accès sécurisé ?", response: "", justification: "" },
                    { id: "q4_2", num: "Q4.2", text: "Tri et évacuation des déchets du chantier conformes aux règles du site ?", response: "", justification: "" }
                ]
            }
        ];

        let auditData = JSON.parse(JSON.stringify(defaultAuditStructure));
        let savedAuditsHistory = [];

        window.onload = function() {
            document.getElementById('audit_date').valueAsDate = new Date();
            loadHistoryFromLocalStorage();
            loadDraftFromLocalStorage();
            renderApp();
            updateGlobalStats();
        };

        function renderApp() {
            renderNav();
            renderQuestions();
            updateScores();
        }

        function renderNav() {
            const navList = document.getElementById('themeNavList');
            navList.innerHTML = '';
            auditData.forEach(theme => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <a href="#${theme.themeId}">
                        <span>${theme.themeTitle}</span>
                        <span class="badge-count">${theme.questions.length}</span>
                    </a>
                `;
                navList.appendChild(li);
            });
        }

        function renderQuestions() {
            const container = document.getElementById('questionsContainer');
            container.innerHTML = '';

            auditData.forEach(theme => {
                const card = document.createElement('div');
                card.className = 'theme-card';
                card.id = theme.themeId;

                let questionsHTML = '';
                theme.questions.forEach(q => {
                    const isC = q.response === 'C' ? 'checked' : '';
                    const isNC = q.response === 'NC' ? 'checked' : '';
                    const isNA = q.response === 'NA' ? 'checked' : '';

                    questionsHTML += `
                        <div class="question-item">
                            <div class="question-text">
                                <span class="question-num">${q.num}</span> ${q.text}
                            </div>
                            <div class="response-options">
                                <label class="option-label opt-c">
                                    <input type="radio" name="resp_${q.id}" value="C" ${isC} onchange="updateResponse('${q.id}', 'C')">
                                    <i class="fa-solid fa-circle-check"></i> Conforme
                                </label>
                                <label class="option-label opt-nc">
                                    <input type="radio" name="resp_${q.id}" value="NC" ${isNC} onchange="updateResponse('${q.id}', 'NC')">
                                    <i class="fa-solid fa-circle-xmark"></i> Non Conforme
                                </label>
                                <label class="option-label opt-na">
                                    <input type="radio" name="resp_${q.id}" value="NA" ${isNA} onchange="updateResponse('${q.id}', 'NA')">
                                    <i class="fa-solid fa-minus-circle"></i> Non Applicable
                                </label>
                            </div>
                            <input type="text" class="justification-input" placeholder="Justification / Remarques..." 
                                   value="${q.justification || ''}" oninput="updateJustification('${q.id}', this.value)">
                        </div>
                    `;
                });

                card.innerHTML = `
                    <div class="theme-card-header">
                        <h3>${theme.themeTitle}</h3>
                    </div>
                    <div>${questionsHTML}</div>
                `;

                container.appendChild(card);
            });
        }

        function updateResponse(questionId, value) {
            for (let theme of auditData) {
                let q = theme.questions.find(item => item.id === questionId);
                if (q) { q.response = value; break; }
            }
            updateScores();
            autoSaveDraft();
        }

        function updateJustification(questionId, value) {
            for (let theme of auditData) {
                let q = theme.questions.find(item => item.id === questionId);
                if (q) { q.justification = value; break; }
            }
            autoSaveDraft();
        }

        function updateScores() {
            let total = 0, countC = 0, countNC = 0, countNA = 0;
            auditData.forEach(theme => {
                theme.questions.forEach(q => {
                    total++;
                    if (q.response === 'C') countC++;
                    else if (q.response === 'NC') countNC++;
                    else if (q.response === 'NA') countNA++;
                });
            });

            document.getElementById('countC').innerText = countC;
            document.getElementById('countNC').innerText = countNC;
            document.getElementById('countNA').innerText = countNA;

            const applicableTotal = countC + countNC;
            const percent = applicableTotal > 0 ? Math.round((countC / applicableTotal) * 100) : 0;
            document.getElementById('scorePercent').innerText = `${percent}%`;
        }

        /* --- SAUVEGARDE LOCALE & DRAFT EN TEMPS RÉEL --- */
        function autoSaveDraft() {
            const draft = {
                eeNom: document.getElementById('ee_nom').value,
                eeIntervenant: document.getElementById('ee_intervenant').value,
                auditeurNom: document.getElementById('auditeur_nom').value,
                auditDate: document.getElementById('audit_date').value,
                eeZone: document.getElementById('ee_zone').value,
                eePdp: document.getElementById('ee_pdp').value,
                auditData: auditData
            };
            localStorage.setItem('current_audit_draft', JSON.stringify(draft));
        }

        function loadDraftFromLocalStorage() {
            const savedDraft = localStorage.getItem('current_audit_draft');
            if (savedDraft) {
                try {
                    const draft = JSON.parse(savedDraft);
                    document.getElementById('ee_nom').value = draft.eeNom || '';
                    document.getElementById('ee_intervenant').value = draft.eeIntervenant || '';
                    document.getElementById('auditeur_nom').value = draft.auditeurNom || '';
                    if (draft.auditDate) document.getElementById('audit_date').value = draft.auditDate;
                    document.getElementById('ee_zone').value = draft.eeZone || '';
                    document.getElementById('ee_pdp').value = draft.eePdp || '';
                    if (draft.auditData) auditData = draft.auditData;
                } catch(e) { console.error("Erreur de chargement du brouillon", e); }
            }
        }

        function saveAndArchiveCurrentAudit() {
            const eeNom = document.getElementById('ee_nom').value.trim();
            if (!eeNom) {
                alert("Veuillez renseigner au moins le nom de l'Entreprise Extérieure (EE) avant d'archiver.");
                return;
            }

            let countC = 0, countNC = 0, countNA = 0;
            auditData.forEach(t => t.questions.forEach(q => {
                if (q.response === 'C') countC++;
                if (q.response === 'NC') countNC++;
                if (q.response === 'NA') countNA++;
            }));
            const appTotal = countC + countNC;
            const scorePercent = appTotal > 0 ? Math.round((countC / appTotal) * 100) : 0;

            const newRecord = {
                id: 'audit_' + Date.now(),
                timestamp: new Date().toISOString(),
                eeNom: eeNom,
                eeIntervenant: document.getElementById('ee_intervenant').value,
                auditeurNom: document.getElementById('auditeur_nom').value || "Léa Dusek",
                auditDate: document.getElementById('audit_date').value,
                eeZone: document.getElementById('ee_zone').value,
                eePdp: document.getElementById('ee_pdp').value,
                scorePercent: scorePercent,
                stats: { countC, countNC, countNA },
                auditData: JSON.parse(JSON.stringify(auditData))
            };

            savedAuditsHistory.unshift(newRecord);
            saveHistoryToLocalStorage();
            updateGlobalStats();
            alert(`L'audit pour "${eeNom}" a été enregistré et archivé avec succès !`);
        }

        function saveHistoryToLocalStorage() {
            localStorage.setItem('saved_audits_history', JSON.stringify(savedAuditsHistory));
        }

        function loadHistoryFromLocalStorage() {
            const data = localStorage.getItem('saved_audits_history');
            if (data) {
                try { savedAuditsHistory = JSON.parse(data); } catch(e) { savedAuditsHistory = []; }
            }
        }

        /* CALCULE ET AFFICHE LE RÉCAPITULATIF (MOYENNE & COMPTE) */
        function updateGlobalStats() {
            const count = savedAuditsHistory.length;
            document.getElementById('savedAuditsCount').innerText = count;
            document.getElementById('totalAuditsCount').innerText = count;
            document.getElementById('modalTotalAudits').innerText = count;

            if (count === 0) {
                document.getElementById('globalAveragePercent').innerText = '-%';
                document.getElementById('modalAvgScore').innerText = '-%';
                return;
            }

            const totalScoreSum = savedAuditsHistory.reduce((sum, item) => sum + item.scorePercent, 0);
            const globalAvg = Math.round(totalScoreSum / count);

            document.getElementById('globalAveragePercent').innerText = `${globalAvg}%`;
            document.getElementById('modalAvgScore').innerText = `${globalAvg}%`;
        }

        /* --- MODALE HISTORIQUE DES AUDITS --- */
        function openHistoryModal() {
            renderHistoryTable();
            document.getElementById('historyModal').classList.add('active');
        }

        function closeHistoryModal() {
            document.getElementById('historyModal').classList.remove('active');
        }

        function renderHistoryTable() {
            const tbody = document.getElementById('historyTableBody');
            tbody.innerHTML = '';

            if (savedAuditsHistory.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-muted); padding:20px;">Aucun audit archivé pour le moment.</td></tr>`;
                return;
            }

            savedAuditsHistory.forEach(record => {
                const tr = document.createElement('tr');
                let badgeClass = "good";
                if (record.scorePercent < 70) badgeClass = "bad";
                else if (record.scorePercent < 85) badgeClass = "medium";

                tr.innerHTML = `
                    <td>${record.auditDate || 'N/C'}</td>
                    <td><strong>${record.eeNom}</strong></td>
                    <td>${record.eeZone || '-'}</td>
                    <td>${record.auditeurNom || '-'}</td>
                    <td><span class="badge-score ${badgeClass}">${record.scorePercent}%</span></td>
                    <td>
                        <div class="action-btns-cell">
                            <button class="btn-sm btn-archive" onclick="loadAuditFromHistory('${record.id}')" title="Consulter/Charger">
                                <i class="fa-solid fa-folder-open"></i> Ouvrir
                            </button>
                            <button class="btn-sm btn-excel" onclick="exportSingleRecordExcel('${record.id}')" title="Télécharger Excel">
                                <i class="fa-solid fa-file-excel"></i> Excel
                            </button>
                            <button class="btn-sm btn-danger" onclick="deleteHistoryRecord('${record.id}')" title="Supprimer">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function loadAuditFromHistory(recordId) {
            const record = savedAuditsHistory.find(r => r.id === recordId);
            if (!record) return;

            if (confirm(`Voulez-vous charger l'audit archivé de "${record.eeNom}" ?`)) {
                document.getElementById('ee_nom').value = record.eeNom || '';
                document.getElementById('ee_intervenant').value = record.eeIntervenant || '';
                document.getElementById('auditeur_nom').value = record.auditeurNom || '';
                document.getElementById('audit_date').value = record.auditDate || '';
                document.getElementById('ee_zone').value = record.eeZone || '';
                document.getElementById('ee_pdp').value = record.eePdp || '';
                
                auditData = JSON.parse(JSON.stringify(record.auditData));
                renderApp();
                autoSaveDraft();
                closeHistoryModal();
            }
        }

        function deleteHistoryRecord(recordId) {
            if (confirm("Voulez-vous vraiment supprimer cet audit de l'historique ?")) {
                savedAuditsHistory = savedAuditsHistory.filter(r => r.id !== recordId);
                saveHistoryToLocalStorage();
                updateGlobalStats();
                renderHistoryTable();
            }
        }

        function exportHistoryJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(savedAuditsHistory, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `Sauvegarde_Base_Audits_HSE_${new Date().toISOString().slice(0,10)}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }

        function importHistoryJSON() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = e => {
                const file = e.target.files[0];
                const reader = new FileReader();
                reader.onload = event => {
                    try {
                        const imported = JSON.parse(event.target.result);
                        if (Array.isArray(imported)) {
                            savedAuditsHistory = imported;
                            saveHistoryToLocalStorage();
                            updateGlobalStats();
                            renderHistoryTable();
                            alert("Base d'audits importée avec succès !");
                        } else { alert("Format JSON invalide."); }
                    } catch(err) { alert("Erreur lors de la lecture du fichier JSON."); }
                };
                reader.readAsText(file);
            };
            input.click();
        }

        function resetForm() {
            if (confirm("Voulez-vous vider la saisie actuelle pour démarrer un NOUVEL audit ?")) {
                document.getElementById('ee_nom').value = '';
                document.getElementById('ee_intervenant').value = '';
                document.getElementById('ee_zone').value = '';
                document.getElementById('ee_pdp').value = '';
                auditData = JSON.parse(JSON.stringify(defaultAuditStructure));
                localStorage.removeItem('current_audit_draft');
                renderApp();
            }
        }

        function openAddQuestionModal() {
            const select = document.getElementById('modal_theme');
            select.innerHTML = '';
            auditData.forEach(theme => {
                const opt = document.createElement('option');
                opt.value = theme.themeId;
                opt.innerText = theme.themeTitle;
                select.appendChild(opt);
            });
            document.getElementById('addModal').classList.add('active');
        }

        function closeAddQuestionModal() { document.getElementById('addModal').classList.remove('active'); }

        function saveNewQuestion() {
            const themeId = document.getElementById('modal_theme').value;
            const num = document.getElementById('modal_qnum').value.trim() || "Q_NEW";
            const text = document.getElementById('modal_qtext').value.trim();

            if (!text) { alert("Veuillez saisir le texte de la question."); return; }

            const theme = auditData.find(t => t.themeId === themeId);
            if (theme) {
                theme.questions.push({ id: 'q_' + Date.now(), num: num, text: text, response: '', justification: '' });
                renderApp();
                autoSaveDraft();
                closeAddQuestionModal();
            }
        }

        /* --- EXPORT EXCEL --- */
        function exportToExcel() {
            const eeNom = document.getElementById('ee_nom').value || "Non précisé";
            const eeIntervenant = document.getElementById('ee_intervenant').value || "Non précisé";
            const auditeurNom = document.getElementById('auditeur_nom').value || "Non précisé";
            const auditDate = document.getElementById('audit_date').value || "Non précisée";
            const eeZone = document.getElementById('ee_zone').value || "Non précisée";
            const eePdp = document.getElementById('ee_pdp').value || "Non précisé";

            generateExcelFile(eeNom, eeIntervenant, auditeurNom, auditDate, eeZone, eePdp, auditData);
        }

        function exportSingleRecordExcel(recordId) {
            const record = savedAuditsHistory.find(r => r.id === recordId);
            if (!record) return;
            generateExcelFile(
                record.eeNom, record.eeIntervenant, record.auditeurNom,
                record.auditDate, record.eeZone, record.eePdp, record.auditData
            );
        }

        function generateExcelFile(eeNom, eeIntervenant, auditeurNom, auditDate, eeZone, eePdp, currentAuditData) {
            let countC = 0, countNC = 0, countNA = 0;
            currentAuditData.forEach(t => t.questions.forEach(q => {
                if (q.response === 'C') countC++;
                if (q.response === 'NC') countNC++;
                if (q.response === 'NA') countNA++;
            }));
            const appTotal = countC + countNC;
            const scorePercent = appTotal > 0 ? Math.round((countC / appTotal) * 100) + "%" : "N/A";

            const excelRows = [];
            excelRows.push(["AUDIT DE SÉCURITÉ - ENTREPRISE EXTÉRIEURE (EE)"]);
            excelRows.push([]);
            excelRows.push(["INFORMATIONS GÉNÉRALES & ENTREPRISE EXTÉRIEURE"]);
            excelRows.push(["Entreprise Extérieure (EE) :", eeNom, "", "Date d'inspection :", auditDate]);
            excelRows.push(["Intervenant / Représentant EE :", eeIntervenant, "", "Auditeur HSE :", auditeurNom]);
            excelRows.push(["Chantier / Zone :", eeZone, "", "N° PDP / Permis :", eePdp]);
            excelRows.push(["Taux de Conformité Global :", scorePercent, "", "Synthèse :", `${countC} Conforme(s) | ${countNC} Non Conforme(s) | ${countNA} N/A`]);
            excelRows.push([]);
            excelRows.push([]);

            excelRows.push(["N°question", "thème", "question", "réponse", "justification"]);

            currentAuditData.forEach(theme => {
                theme.questions.forEach(q => {
                    let libelleReponse = "Non renseigné";
                    if (q.response === 'C') libelleReponse = "Conforme";
                    else if (q.response === 'NC') libelleReponse = "Non Conforme";
                    else if (q.response === 'NA') libelleReponse = "Non Applicable";

                    excelRows.push([
                        q.num,
                        theme.themeTitle,
                        q.text,
                        libelleReponse,
                        q.justification || ""
                    ]);
                });
            });

            const ws = XLSX.utils.aoa_to_sheet(excelRows);
            ws['!cols'] = [
                { wch: 14 },
                { wch: 35 },
                { wch: 65 },
                { wch: 18 },
                { wch: 50 }
            ];

            ws['!merges'] = [
                { s: { r: 0, c: 0 }, e: { r: 0, c: 4 } },
                { s: { r: 2, c: 0 }, e: { r: 2, c: 4 } }
            ];

            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Audit HSE EE");

            const cleanEename = eeNom.replace(/[^a-zA-Z0-9]/g, "_");
            XLSX.writeFile(wb, `Audit_HSE_EE_${cleanEename}_${auditDate}.xlsx`);
        }
    </script>
</body>
</html>
