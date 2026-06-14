"""
PsychoCrowd — Streamlit Dashboard Premium v2
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
from config import *
from src.data_loader import classify_domain

st.set_page_config(
    page_title="PsychoCrowd | AI Psychometrics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Translations ──────────────────────────────────────────────────────
TEXTS = {
    "English": {
        "sidebar_subtitle": "AI Psychometric Engine",
        "lang_select": "🌐 Language",
        "data_import": "📂 Data Import",
        "mcq_bank": "MCQ Bank (CSV)",
        "mcq_help": "Upload your question bank.",
        "human_resp": "Human Responses (CSV)",
        "human_help": "Upload real student data to compare with AI.",
        "crowd_params": "👥 Crowd Parameters",
        "n_per_profile": "Students per profile",
        "n_help": "Number of synthetic students to generate for each ability tier.",
        "engine_config": "🤖 Engine Configuration",
        "enable_gemini": "Enable Google Gemini API",
        "api_key": "Gemini API Key",
        "launch_btn": "🚀 LAUNCH SIMULATION",
        "dash_title": "Dashboard Overview",
        "dash_desc": "Analyze and compare artificial intelligence problem-solving with real human behavior using the Rasch psychometric model.",
        "tab_mcq": "📚 Item Bank",
        "tab_crowd": "👥 Synthetic Crowd",
        "tab_rasch": "📊 Rasch Engine",
        "tab_val": "🔬 Validation",
        "tab_student": "🔎 Student Lookup",
        "tab_insights": "💡 AI Insights",
        "tab_help": "❓ Help Center",
        "tab_guide": "📖 User Guide",
        "guide_title": "📖 User Guide & SOP",
        "insights_title": "💡 Pedagogical Insights",
        "context_title": "📚 Global Test Context",
        "item_bank_title": "📚 Item Bank Overview",
        "total_items": "Total Items",
        "easy_items": "Easy Items",
        "medium_items": "Medium Items",
        "hard_items": "Hard Items",
        "item_preview": "### Item Preview",
        "crowd_title": "👥 Synthetic Student Crowd",
        "resp_heatmap": "### Response Heatmap",
        "mean_acc": "### Mean Accuracy by Profile",
        "run_first": "ℹ️ Run the simulation first to see results here.",
        "rasch_title": "📊 Item Response Theory (1PL Rasch)",
        "human_students": "🙋‍♂️ Human Students",
        "art_crowd": "🤖 Artificial Crowd",
        "converged": "Converged",
        "iterations": "Iterations",
        "yes": "✅ Yes", "no": "❌ No",
        "mean_ability": "Mean Ability",
        "mean_diff": "Mean Difficulty",
        "std_ability": "Std Ability",
        "std_diff": "Std Difficulty",
        "logits": "logits",
        "wright_map": "### Wright Map (Person-Item Distribution)",
        "rasch_run_first": "ℹ️ Run the simulation to view Rasch analysis.",
        "val_title": "🔬 Psychometric Validation",
        "pearson": "Pearson r",
        "spearman": "Spearman ρ",
        "mae": "MAE",
        "val_status": "Verdict",
        "download_json": "📥 Download JSON Report",
        "val_run_first": "ℹ️ Run the simulation to view validation metrics.",
        "running_msg": "⏳ Running simulation pipeline...",
        "success_msg": "✨ Simulation complete! Dashboard updated.",
        "student_lookup_title": "🔎 Student Profile",
        "select_student": "Select a Student ID",
        "student_not_found": "Student data not available.",
        "student_accuracy": "Overall Accuracy",
        "student_profile": "Profile / Category",
        "student_details": "Item-Level Responses",
        "help_title": "❓ Help Center",
        "version_label": "v2.1 — Premium",
    },
    "Français": {
        "sidebar_subtitle": "Moteur Psychométrique IA",
        "lang_select": "🌐 Langue",
        "data_import": "📂 Import des Données",
        "mcq_bank": "Banque QCM (CSV)",
        "mcq_help": "Importez votre banque de questions.",
        "human_resp": "Réponses Humaines (CSV)",
        "human_help": "Importez les vraies réponses pour comparer avec l'IA.",
        "crowd_params": "👥 Paramètres de Foule",
        "n_per_profile": "Étudiants par profil",
        "n_help": "Nombre d'étudiants synthétiques par niveau.",
        "engine_config": "🤖 Configuration Moteur",
        "enable_gemini": "Activer l'API Gemini",
        "api_key": "Clé API Gemini",
        "launch_btn": "🚀 LANCER LA SIMULATION",
        "dash_title": "Tableau de Bord",
        "dash_desc": "Analysez et comparez la résolution de problèmes de l'IA avec le comportement humain réel via le modèle psychométrique de Rasch.",
        "tab_mcq": "📚 Banque d'Items",
        "tab_crowd": "👥 Foule Synthétique",
        "tab_rasch": "📊 Moteur Rasch",
        "tab_val": "🔬 Validation",
        "tab_student": "🔎 Recherche Élève",
        "tab_insights": "💡 Recommandations IA",
        "tab_help": "❓ Centre d'Aide",
        "tab_guide": "📖 Guide d'Utilisation",
        "guide_title": "📖 Guide d'Utilisation & SOP",
        "insights_title": "💡 Recommandations Pédagogiques",
        "context_title": "📚 Contexte Global du Test",
        "item_bank_title": "📚 Aperçu de la Banque d'Items",
        "total_items": "Total Items",
        "easy_items": "Items Faciles",
        "medium_items": "Items Moyens",
        "hard_items": "Items Difficiles",
        "item_preview": "### Aperçu des Items",
        "crowd_title": "👥 Foule d'Étudiants Synthétiques",
        "resp_heatmap": "### Carte de Chaleur des Réponses",
        "mean_acc": "### Précision Moyenne par Profil",
        "run_first": "ℹ️ Lancez la simulation pour afficher les résultats.",
        "rasch_title": "📊 Théorie de Réponse à l'Item (Rasch 1PL)",
        "human_students": "🙋‍♂️ Étudiants Humains",
        "art_crowd": "🤖 Foule Artificielle",
        "converged": "Convergence",
        "iterations": "Itérations",
        "yes": "✅ Oui", "no": "❌ Non",
        "mean_ability": "Compétence Moy.",
        "mean_diff": "Difficulté Moy.",
        "std_ability": "Écart-type Comp.",
        "std_diff": "Écart-type Diff.",
        "logits": "logits",
        "wright_map": "### Carte de Wright (Personne-Item)",
        "rasch_run_first": "ℹ️ Lancez la simulation pour voir l'analyse Rasch.",
        "val_title": "🔬 Validation Psychométrique",
        "pearson": "Pearson r",
        "spearman": "Spearman ρ",
        "mae": "EAM",
        "val_status": "Verdict",
        "download_json": "📥 Télécharger le Rapport JSON",
        "val_run_first": "ℹ️ Lancez la simulation pour les métriques.",
        "running_msg": "⏳ Simulation en cours...",
        "success_msg": "✨ Simulation terminée ! Résultats mis à jour.",
        "student_lookup_title": "🔎 Profil de l'Élève",
        "select_student": "Sélectionnez un ID d'élève",
        "student_not_found": "Données de l'élève non disponibles.",
        "student_accuracy": "Précision Globale",
        "student_profile": "Profil / Catégorie",
        "student_details": "Réponses par Item",
        "help_title": "❓ Centre d'Aide",
        "version_label": "v2.1 — Premium",
    }
}

# ── Premium CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(180deg, #F0F4F8 0%, #F8FAFC 40%, #FFFFFF 100%); }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Typography ── */
    h1 { font-weight: 800 !important; color: #0F172A !important; letter-spacing: -0.03em; }
    h2 { font-weight: 700 !important; color: #1E293B !important; letter-spacing: -0.02em; margin-top: 0.5rem !important; }
    h3 { font-weight: 600 !important; color: #334155 !important; }
    p, .stMarkdown { color: #475569; line-height: 1.6; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e0c0e 0%, #3a151b 100%) !important;
        border-right: none;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span {
        color: #CBD5E1 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #F1F5F9;
        border-radius: 12px;
        padding: 4px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 0.85rem;
        color: #64748B;
        border-bottom: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #722F37 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-bottom: none !important;
    }

    /* ── Cards ── */
    .premium-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .premium-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 4px 10px rgba(0,0,0,0.04);
        border-color: #CBD5E1;
    }
    .card-title {
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .card-value {
        color: #0F172A;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .card-subtitle {
        color: #94A3B8;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 4px;
    }

    /* ── Status Colors ── */
    .status-excellent { color: #059669; }
    .status-good { color: #10B981; }
    .status-fair { color: #F59E0B; }
    .status-poor { color: #EF4444; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 12px 24px !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-baseweb="button"] {
        background: linear-gradient(135deg, #722F37 0%, #9a3f4a 50%, #b84c5a 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(114, 47, 55, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-baseweb="button"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(114, 47, 55, 0.45) !important;
    }

    /* ── Hero Header ── */
    .hero-header {
        background: linear-gradient(135deg, #722F37 0%, #4a1f24 40%, #2a1114 100%);
        border-radius: 20px;
        padding: 36px 40px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '∫x';
        font-family: serif;
        font-weight: 800;
        font-size: 20rem;
        color: rgba(255,255,255,0.05);
        position: absolute;
        top: -100px;
        right: -40px;
        line-height: 1;
    }
    .hero-header h1 {
        color: #FFFFFF !important;
        font-size: 2rem;
        margin-bottom: 6px;
        position: relative;
    }
    .hero-header p {
        color: #94A3B8 !important;
        font-size: 1rem;
        position: relative;
        max-width: 700px;
    }

    /* ── Help Center ── */
    .help-section {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        transition: all 0.2s ease;
    }
    .help-section:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .help-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    .help-badge {
        display: inline-block;
        background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
        color: #4338CA;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    /* ── Glassmorphism info boxes ── */
    .glass-info {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226,232,240,0.8);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }

    /* ── Version Badge ── */
    .version-badge {
        display: inline-block;
        background: linear-gradient(135deg, #722F37, #b84c5a);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    /* ── Sections ── */
    .section-title {
        color: #722F37;
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 40px;
        margin-bottom: 20px;
        border-bottom: 3px solid #722F37;
        padding-bottom: 10px;
        display: inline-block;
    }
    .section-divider {
        height: 60px;
    }
    .stDataFrame { border-radius: 12px; overflow: hidden; }

</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    lang_choice = st.selectbox("🌐", ["English", "Français"], index=1, label_visibility="collapsed")
    T = TEXTS[lang_choice]

    st.markdown(f"""
        <div style='text-align: center; margin: 1.5rem 0 1rem;'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 15px;'>
                <div style='font-size: 3rem; font-weight: 800; color: white; line-height: 1; display: flex; align-items: center;'>
                    <span style='font-family: Georgia, serif; font-size: 4.5rem; font-style: italic; margin-right: 4px; transform: translateY(-4px); display: inline-block;'>∫</span>
                    <span style='font-family: "Inter", sans-serif; font-size: 2.5rem; transform: translateY(4px); display: inline-block;'>x</span>
                </div>
                <div style='width: 2px; height: 45px; background-color: white; border-radius: 2px;'></div>
                <div style='text-align: left; display: flex; flex-direction: column; justify-content: center;'>
                    <h1 style='color: #FFFFFF !important; margin: 0 0 2px 0; font-size: 1.3rem; font-weight: 800; letter-spacing: 0.05em; line-height: 1;'>PSYCHOCROWD</h1>
                    <span style='color: #FFFFFF !important; font-size: 0.42rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase;'>DECIPHER CROWDS, ANTICIPATE TRENDS</span>
                </div>
            </div>
            <span class='version-badge'>{T["version_label"]}</span>
        </div>
    """, unsafe_allow_html=True)

# ── Hero Header ───────────────────────────────────────────────────────
st.markdown(f"""
    <div class='hero-header'>
        <h1>🧠 {T['dash_title']}</h1>
        <p>{T['dash_desc']}</p>
    </div>
""", unsafe_allow_html=True)

# ── Configuration & Data Import ───────────────────────────────────────
with st.container():
    st.markdown(f"### ⚙️ {T['data_import']} & Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**1. {T['mcq_bank']}**")
        mcq_file = st.file_uploader("", type="csv", help=T["mcq_help"], key="mcq")
        
        st.markdown(f"**2. {T['human_resp']}**")
        human_file = st.file_uploader("", type="csv", help=T["human_help"], key="human")
        
    with col2:
        st.markdown(f"**3. {T['crowd_params']}**")
        n_per_profile = st.slider(
            T["n_per_profile"], 10, 100, N_STUDENTS_PER_PROFILE, 10, help=T["n_help"]
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**4. {T['engine_config']}**")
        use_gemini = st.toggle(T["enable_gemini"], value=True)
        if use_gemini:
            api_key = st.text_input(T["api_key"], type="password", placeholder="AIzaSy...")
            
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        run_btn = st.button(T["launch_btn"], use_container_width=True)
    st.markdown("<hr style='margin: 1rem 0 2rem 0;'>", unsafe_allow_html=True)

# ── Sections de la Plateforme (Ex-Tabs) ──────────────────────────────────
# Nous remplaçons les onglets par des conteneurs verticaux espacés.
tab1 = st.container()
tab2 = st.container()
tab3 = st.container()
tab4 = st.container()
tab5 = st.container()
tab6 = st.container()
tab7 = st.container()
tab8 = st.container()

# ── Helper: load existing outputs ──────────────────────────────────────
report_path = OUTPUTS_DIR / "full_report.json"
response_path = OUTPUTS_DIR / "response_matrix.csv"
comparison_path = OUTPUTS_DIR / "rasch_comparison.csv"
has_outputs = report_path.exists()


# ═══════════════════════════════════════════════════════════════════════
# TAB 1 — MCQ Bank
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='section-title'>{T['item_bank_title']}</h2>", unsafe_allow_html=True)
    from src.data_loader import load_mcq_bank
    if mcq_file is not None:
        mcq_file.seek(0)
        try:
            mcq_df = pd.read_csv(mcq_file, sep=None, engine="python")
        except UnicodeDecodeError:
            mcq_file.seek(0)
            mcq_df = pd.read_csv(mcq_file, sep=None, engine="python", encoding="latin1")
        if "item_id" not in mcq_df.columns:
            mcq_df["item_id"] = range(len(mcq_df))
    else:
        mcq_df = load_mcq_bank(MCQ_PATH)

    # Metric Cards
    easy_count = int((mcq_df["difficulty_expert"] == "easy").sum()) if "difficulty_expert" in mcq_df.columns else 0
    medium_count = int((mcq_df["difficulty_expert"] == "medium").sum()) if "difficulty_expert" in mcq_df.columns else 0
    hard_count = int((mcq_df["difficulty_expert"] == "hard").sum()) if "difficulty_expert" in mcq_df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class='premium-card'>
                <div class='card-title'>{T["total_items"]}</div>
                <div class='card-value'>{len(mcq_df)}</div>
                <div class='card-subtitle'>questions chargées</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='premium-card' style='border-top: 3px solid #10B981;'>
                <div class='card-title'>{T["easy_items"]}</div>
                <div class='card-value' style='color: #059669;'>{easy_count}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class='premium-card' style='border-top: 3px solid #F59E0B;'>
                <div class='card-title'>{T["medium_items"]}</div>
                <div class='card-value' style='color: #D97706;'>{medium_count}</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class='premium-card' style='border-top: 3px solid #EF4444;'>
                <div class='card-title'>{T["hard_items"]}</div>
                <div class='card-value' style='color: #DC2626;'>{hard_count}</div>
            </div>
        """, unsafe_allow_html=True)

    # Difficulty distribution chart
    if "difficulty_expert" in mcq_df.columns:
        import plotly.express as px
        diff_counts = mcq_df["difficulty_expert"].value_counts().reindex(["easy", "medium", "hard"], fill_value=0)
        fig_diff = px.pie(
            names=diff_counts.index.str.capitalize(),
            values=diff_counts.values,
            color=diff_counts.index,
            color_discrete_map={"easy": "#10B981", "medium": "#F59E0B", "hard": "#EF4444"},
            hole=0.55
        )
        fig_diff.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            font=dict(family="Inter", color="#334155")
        )
        fig_diff.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_diff, use_container_width=True)

    st.markdown(T["item_preview"])
    st.dataframe(mcq_df.head(15), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════
# TAB 2 — Artificial Crowd
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    if has_outputs and response_path.exists():
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='section-title'>{T['crowd_title']}</h2>", unsafe_allow_html=True)
        crowd_df = pd.read_csv(response_path)

        # Summary cards
        if "profile" in crowd_df.columns and "is_correct" in crowd_df.columns:
            profiles_list = crowd_df["profile"].unique()
            cols = st.columns(len(profiles_list))
            profile_colors = {"expert": "#2563EB", "good": "#10B981", "medium": "#F59E0B", "weak": "#EF4444"}
            for idx, profile in enumerate(sorted(profiles_list)):
                acc = crowd_df[crowd_df["profile"] == profile]["is_correct"].mean()
                color = profile_colors.get(profile, "#64748B")
                with cols[idx]:
                    st.markdown(f"""
                        <div class='premium-card' style='border-top: 3px solid {color}; text-align: center;'>
                            <div class='card-title'>{profile.upper()}</div>
                            <div class='card-value' style='color: {color};'>{acc:.0%}</div>
                            <div class='card-subtitle'>accuracy</div>
                        </div>
                    """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(T["resp_heatmap"])
            import plotly.express as px
            sample_students = crowd_df["student_id"].unique()[:40]
            sample_items = sorted(crowd_df["item_id"].unique()[:40])
            sample = crowd_df[
                crowd_df["student_id"].isin(sample_students) &
                crowd_df["item_id"].isin(sample_items)
            ]
            if len(sample) > 0 and "is_correct" in sample.columns:
                pivot = sample.pivot_table(
                    index="student_id", columns="item_id",
                    values="is_correct", fill_value=0
                )
                fig = px.imshow(pivot.values,
                                color_continuous_scale=["#FCA5A5", "#34D399"],
                                labels=dict(color="Correct"),
                                aspect="auto")
                fig.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False,
                    font=dict(family="Inter")
                )
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown(T["mean_acc"])
            if "profile" in crowd_df.columns and "is_correct" in crowd_df.columns:
                acc = crowd_df.groupby("profile")["is_correct"].mean().reset_index()
                fig2 = px.bar(acc, x="profile", y="is_correct", color="profile",
                              color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B", "#EF4444"])
                fig2.update_layout(
                    showlegend=False, xaxis_title=None, yaxis_title="Accuracy",
                    font=dict(family="Inter"),
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                fig2.update_traces(marker_line_width=0, marker_cornerradius=6)
                st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# TAB 3 — Rasch Analysis
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    if has_outputs:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='section-title'>{T['rasch_title']}</h2>", unsafe_allow_html=True)
        report = json.loads(report_path.read_text())

        c1, c2 = st.columns(2)
        with c1:
            h = report.get("human_rasch", {})
            st.markdown(f"""
                <div class='premium-card' style='border-left: 4px solid #E63946;'>
                    <h3 style='margin-top:0;'>{T["human_students"]}</h3>
                    <table style='width:100%; border-collapse: collapse;'>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["converged"]}</td><td style='text-align:right; font-weight:600;'>{T['yes'] if h.get('converged') else T['no']}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["iterations"]}</td><td style='text-align:right; font-weight:600;'>{h.get('n_iterations', '—')}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["mean_ability"]}</td><td style='text-align:right; font-weight:600;'>{h.get('mean_ability', 0):.3f} {T["logits"]}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["mean_diff"]}</td><td style='text-align:right; font-weight:600;'>{h.get('mean_difficulty', 0):.3f} {T["logits"]}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["std_ability"]}</td><td style='text-align:right; font-weight:600;'>{h.get('std_ability', 0):.3f}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["std_diff"]}</td><td style='text-align:right; font-weight:600;'>{h.get('std_difficulty', 0):.3f}</td></tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            a = report.get("art_rasch", {})
            st.markdown(f"""
                <div class='premium-card' style='border-left: 4px solid #2EC4B6;'>
                    <h3 style='margin-top:0;'>{T["art_crowd"]}</h3>
                    <table style='width:100%; border-collapse: collapse;'>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["converged"]}</td><td style='text-align:right; font-weight:600;'>{T['yes'] if a.get('converged') else T['no']}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["iterations"]}</td><td style='text-align:right; font-weight:600;'>{a.get('n_iterations', '—')}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["mean_ability"]}</td><td style='text-align:right; font-weight:600;'>{a.get('mean_ability', 0):.3f} {T["logits"]}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["mean_diff"]}</td><td style='text-align:right; font-weight:600;'>{a.get('mean_difficulty', 0):.3f} {T["logits"]}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["std_ability"]}</td><td style='text-align:right; font-weight:600;'>{a.get('std_ability', 0):.3f}</td></tr>
                        <tr><td style='padding:6px 0; color:#64748B;'>{T["std_diff"]}</td><td style='text-align:right; font-weight:600;'>{a.get('std_difficulty', 0):.3f}</td></tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(T["wright_map"])
        wright_path = PLOTS_DIR / "wright_map.png"
        if wright_path.exists():
            st.image(str(wright_path), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# TAB 4 — Validation
# ═══════════════════════════════════════════════════════════════════════
with tab4:
    if has_outputs:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='section-title'>{T['val_title']}</h2>", unsafe_allow_html=True)
        report = json.loads(report_path.read_text())
        metrics = report.get("comparison", {})

        pr = metrics.get("pearson_r", 0)
        sr = metrics.get("spearman_r", 0)
        mae = metrics.get("mae", 0)
        interp = metrics.get("interpretation", "N/A")

        def get_status_class(val, is_error=False):
            if is_error:
                return "status-excellent" if val < 0.5 else ("status-fair" if val < 0.75 else "status-poor")
            return "status-excellent" if val >= 0.9 else ("status-good" if val >= 0.75 else "status-poor")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
                <div class='premium-card'>
                    <div class='card-title'>{T["pearson"]}</div>
                    <div class='card-value {get_status_class(pr)}'>{pr:.4f}</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class='premium-card'>
                    <div class='card-title'>{T["spearman"]}</div>
                    <div class='card-value {get_status_class(sr)}'>{sr:.4f}</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class='premium-card'>
                    <div class='card-title'>{T["mae"]}</div>
                    <div class='card-value {get_status_class(mae, True)}'>{mae:.4f}</div>
                </div>
            """, unsafe_allow_html=True)
        with c4:
            interp_color = "status-excellent" if interp == "Excellent" else ("status-good" if interp == "Good" else "status-poor")
            st.markdown(f"""
                <div class='premium-card'>
                    <div class='card-title'>{T["val_status"]}</div>
                    <div class='card-value {interp_color}'>{interp}</div>
                </div>
            """, unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            scatter_path = PLOTS_DIR / "scatter_comparison.png"
            if scatter_path.exists():
                st.image(str(scatter_path), use_container_width=True)
        with sc2:
            diff_path = PLOTS_DIR / "difficulty_distribution.png"
            if diff_path.exists():
                st.image(str(diff_path), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            st.download_button(
                label=T["download_json"],
                data=report_path.read_text(),
                file_name="psychocrowd_report.json",
                mime="application/json",
                use_container_width=True
            )


# ═══════════════════════════════════════════════════════════════════════
# TAB 5 — Student Lookup
# ═══════════════════════════════════════════════════════════════════════
with tab5:
    if has_outputs and response_path.exists():
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='section-title'>{T['student_lookup_title']}</h2>", unsafe_allow_html=True)
        lookup_df = pd.read_csv(response_path)

    from src.data_loader import load_human_responses
    mcq_df_tmp = None
    if mcq_file is not None:
        mcq_file.seek(0)
        try:
            mcq_df_tmp = pd.read_csv(mcq_file, sep=None, engine="python")
        except UnicodeDecodeError:
            mcq_file.seek(0)
            mcq_df_tmp = pd.read_csv(mcq_file, sep=None, engine="python", encoding="latin1")
        if "item_id" not in mcq_df_tmp.columns:
            mcq_df_tmp["item_id"] = range(len(mcq_df_tmp))
    else:
        from src.data_loader import load_mcq_bank
        mcq_df_tmp = load_mcq_bank(MCQ_PATH)

    # Classify domains for temporary mcq list
    mcq_df_tmp["domain"] = mcq_df_tmp["question"].apply(classify_domain)

    human_df = load_human_responses(HUMAN_PATH, mcq_df_tmp)
    if not human_df.empty:
        human_df["profile"] = "Human"
        if lookup_df is not None:
            human_df_aligned = human_df.rename(columns={"response": "is_correct"})
            for col in ["difficulty", "chosen_option"]:
                if col not in human_df_aligned.columns:
                    human_df_aligned[col] = "Unknown"
            common_cols = ["student_id", "profile", "item_id", "is_correct", "difficulty", "chosen_option"]
            h_subset = human_df_aligned[common_cols] if all(c in human_df_aligned.columns for c in common_cols) else human_df_aligned
            lookup_df = pd.concat([lookup_df, h_subset], ignore_index=True)
        else:
            lookup_df = human_df.rename(columns={"response": "is_correct"})

    if lookup_df is not None and not lookup_df.empty:
        all_students = sorted(lookup_df["student_id"].unique())
        selected_student = st.selectbox(T["select_student"], all_students)

        student_data = lookup_df[lookup_df["student_id"] == selected_student]
        profile = student_data["profile"].iloc[0] if "profile" in student_data.columns else "N/A"

        # Load ability (theta) from report if available
        theta = 0.0
        if has_outputs:
            try:
                report = json.loads(report_path.read_text())
                if profile == "Human":
                    theta = report.get("human_thetas", {}).get(selected_student, 0.0)
                else:
                    theta = report.get("art_thetas", {}).get(selected_student, 0.0)
            except Exception:
                pass

        # Load difficulties for all items
        item_diffs = {}
        if has_outputs and comparison_path.exists():
            try:
                comp_df = pd.read_csv(comparison_path)
                b_col = "b_human" if profile == "Human" else "b_artificial"
                item_diffs = comp_df.set_index("item_id")[b_col].to_dict()
            except Exception:
                pass
        
        if not item_diffs:
            item_diffs = {row["item_id"]: (1.0 if row["difficulty_expert"] == "hard" else (-1.0 if row["difficulty_expert"] == "easy" else 0.0)) for _, row in mcq_df_tmp.iterrows()}

        # Build prediction mapping using IRT logistic model: P = 1 / (1 + exp(-(theta - b)))
        predictions = []
        for _, row in mcq_df_tmp.iterrows():
            iid = row["item_id"]
            b_j = item_diffs.get(iid, 0.0)
            p_success = 1.0 / (1.0 + np.exp(-(theta - b_j)))
            predictions.append({
                "item_id": iid,
                "question": row["question"],
                "correct_option": row["correct_option"],
                "difficulty": row["difficulty_expert"],
                "domain": row["domain"],
                "predicted_probability": p_success
            })
        pred_df = pd.DataFrame(predictions)

        # UI LAYOUT
        c1, c2 = st.columns([2, 3])
        
        with c1:
            st.markdown("### 👤 Profil & Compétence Latente")
            acc = student_data["is_correct"].mean()
            acc_color = "#059669" if acc >= 0.7 else ("#F59E0B" if acc >= 0.5 else "#EF4444")
            
            st.markdown(f"""
                <div class='premium-card' style='border-top: 3px solid {acc_color};'>
                    <div class='card-title'>Précision Actuelle / Actual Accuracy</div>
                    <div class='card-value' style='color: {acc_color};'>{acc:.1%}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class='premium-card' style='border-top: 3px solid #7C3AED;'>
                    <div class='card-title'>Profil / Category</div>
                    <div class='card-value' style='color: #7C3AED;'>{profile.upper()}</div>
                </div>
            """, unsafe_allow_html=True)

            theta_color = "#2563EB" if theta >= 0 else "#EF4444"
            st.markdown(f"""
                <div class='premium-card' style='border-top: 3px solid {theta_color};'>
                    <div class='card-title'>Compétence IRT (θ) / IRT Ability</div>
                    <div class='card-value' style='color: {theta_color};'>{theta:+.3f}</div>
                    <div class='card-subtitle'>mesurée en logits (zéro = moyenne)</div>
                </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("### 🔮 Prédictions & Pronostics de Performance")
            
            # Forecasted success rates by difficulty level
            diff_pred = pred_df.groupby("difficulty")["predicted_probability"].mean().reindex(["easy", "medium", "hard"], fill_value=0.5)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Taux Faciles Prédit", f"{diff_pred['easy']:.0%}")
            with col_b:
                st.metric("Taux Moyens Prédit", f"{diff_pred['medium']:.0%}")
            with col_c:
                st.metric("Taux Difficiles Prédit", f"{diff_pred['hard']:.0%}")
                
            # Domain-Specific Forecast
            domain_pred = pred_df.groupby("domain")["predicted_probability"].mean().reset_index()
            import plotly.express as px
            fig_domain = px.bar(
                domain_pred, 
                x="predicted_probability", 
                y="domain", 
                orientation='h',
                labels={"predicted_probability": "Taux de réussite prédit (0-1)", "domain": "Domaine Mathématique"},
                color="predicted_probability",
                color_continuous_scale="RdYlGn"
            )
            fig_domain.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=220,
                coloraxis_showscale=False,
                font=dict(family="Inter"),
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 1])
            )
            st.plotly_chart(fig_domain, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🎯 Pronostic d'Échecs et Alertes (Top 5 items les plus à risque)")
        
        # Sort by lowest predicted success probability to show highest risks
        highest_risks = pred_df.sort_values(by="predicted_probability").head(5)
        
        for idx, risk_row in highest_risks.iterrows():
            prob = risk_row["predicted_probability"]
            # Color based on risk level
            risk_color = "#EF4444" if prob < 0.25 else ("#F59E0B" if prob < 0.5 else "#10B981")
            
            # Formulate action recommendation based on domain
            rec_text = "Revoir les bases mathématiques associées."
            if risk_row["domain"] == "Calculus":
                rec_text = "Étudier les règles de dérivation en cascade et les formules trigonométriques complexes."
            elif risk_row["domain"] == "Complex Numbers":
                rec_text = "Revoir la définition du module d'un nombre complexe et les représentations géométriques."
            elif risk_row["domain"] == "Algebra & Polynomials":
                rec_text = "S'exercer sur la factorisation d'identités remarquables et les équations quadratiques."
            elif risk_row["domain"] == "Geometry":
                rec_text = "Retravailler les formules d'aires classiques (cercle, triangles) et la formule de distance d'Euclide."
            elif risk_row["domain"] == "Arithmetic":
                rec_text = "Revoir le calcul fractionnaire et les règles de priorités opératoires."
                
            st.markdown(f"""
                <div style='background: #FFFFFF; border-left: 4px solid {risk_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                        <span style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748B;'>
                            Domaine : {risk_row['domain']} | Difficulté : {risk_row['difficulty']}
                        </span>
                        <span style='font-weight: 700; color: {risk_color};'>
                            Probabilité de réussite : {prob:.0%}
                        </span>
                    </div>
                    <p style='margin: 0 0 6px 0; color: #1E293B; font-weight: 500;'><b>Question :</b> {risk_row['question']}</p>
                    <p style='margin: 0 0 6px 0; font-size: 0.85rem; color: #059669;'><b>Réponse attendue :</b> Option {risk_row['correct_option']}</p>
                    <p style='margin: 0; font-size: 0.85rem; color: #475569; background: #F8FAFC; padding: 6px 10px; border-radius: 4px;'>
                        💡 <b>Recommandation de remédiation :</b> {rec_text}
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### {T['student_details']}")
        display_cols = ["item_id", "is_correct"]
        if "difficulty" in student_data.columns: display_cols.append("difficulty")
        if "chosen_option" in student_data.columns: display_cols.append("chosen_option")
        st.dataframe(student_data[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info(T["student_not_found"])


# ═══════════════════════════════════════════════════════════════════════
# TAB 6 — AI Insights
# ═══════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown(f"## {T['insights_title']}")
    if has_outputs:
        report = json.loads(report_path.read_text())

        st.markdown(f"### {T['context_title']}")
        context = report.get("context_summary", "")
        if context and context != "Mock data context.":
            st.markdown(f"""
                <div class='glass-info'>
                    <p style='margin:0; font-size: 1rem; color: #334155;'>{context}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Activez l'API Gemini pour obtenir une analyse contextuelle du test.")

        recs = report.get("ai_recommendations", [])
        if recs:
            st.markdown("### 🎯 Analyse des erreurs fréquentes")
            for rec in recs:
                acc_color = "#EF4444" if rec['accuracy'] < 0.3 else ("#F59E0B" if rec['accuracy'] < 0.6 else "#10B981")
                st.markdown(f"""
                <div class='premium-card' style='border-left: 4px solid {acc_color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                        <h4 style='margin:0; color:#1E293B;'>Question {rec['item_id']}</h4>
                        <span style='background: {acc_color}15; color: {acc_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;'>
                            {rec['accuracy']:.0%} réussite
                        </span>
                    </div>
                    <p style='color:#475569; margin-bottom: 8px;'><b>📝</b> {rec['question']}</p>
                    <p style='margin-bottom: 12px;'>
                        <span style='color: #059669; font-weight: 600;'>✓ {rec['correct']}</span>
                        &nbsp;→&nbsp;
                        <span style='color: #EF4444; font-weight: 600;'>✗ {rec['common_mistake']} (piège)</span>
                    </p>
                    <div style='background: linear-gradient(135deg, #EEF2FF, #F0F9FF); padding: 16px; border-radius: 12px;'>
                        <p style='margin:0; color: #1E293B;'>💡 <b>Recommandation :</b> {rec['ai_recommendation']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Activez l'API Gemini et relancez la simulation pour obtenir des recommandations pédagogiques.")
    else:
        st.info(T["run_first"])


# ═══════════════════════════════════════════════════════════════════════
# TAB 7 — Help Center & Guided Tutorial
# ═══════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown(f"## {T['help_title']}")

    if lang_choice == "Français":
        st.markdown("""
            <div class='glass-info' style='margin-bottom: 24px;'>
                <p style='margin:0; font-size: 1.05rem; color: #1E293B;'>
                    <b>🎓 Tutoriel Guidé de A à Z — Maîtriser PsychoCrowd</b><br>
                    Suivez les étapes ci-dessous pour utiliser PsychoCrowd au maximum de ses capacités statistiques et prédictives.
                </p>
            </div>
        """, unsafe_allow_html=True)

        step_t = st.tabs(["1️⃣ Préparation des Données", "2️⃣ Paramétrage & Simulation", "3️⃣ Analyse Statistique (Rasch)", "4️⃣ Moteur de Prédictions & Pronostics"])

        with step_t[0]:
            st.markdown("""
            ### 📂 Étape 1 : Préparation et Importation des Fichiers CSV
            Pour que l'outil fonctionne, vous pouvez importer deux types de données depuis la barre latérale gauche :
            
            1. **Banque QCM (`mcq_bank.csv`)** :
               - *Fichier requis pour changer les questions.*
               - Format supporté : séparateur `;` ou `,`.
               - **En-têtes attendus** : `Question` (texte), `Choice_A`, `Choice_B`, `Choice_C`, `Choice_D` (options de réponse), `Correct_Answer` (A, B, C ou D), et `Difficulty` (Easy, Medium, ou Hard).
               
            2. **Réponses Humaines (`human_responses.csv`)** :
               - *Optionnel.* Permet de comparer l'IA aux élèves réels et de réaliser des prédictions sur ces élèves.
               - **En-têtes attendus** : `student_id` (nom ou id de l'élève), `item_id` (index de la question de 0 à 999), et `response` (0 pour incorrect, 1 pour correct).
            
            > 💡 **Si vous n'avez pas de données sous la main**, laissez les champs vides. PsychoCrowd va automatiquement générer **1000 questions mathématiques réalistes** et des réponses simulées de **200 élèves** pour tester la plateforme.
            """)

        with step_t[1]:
            st.markdown("""
            ### 🚀 Étape 2 : Configuration du Moteur et Lancement
            Une fois vos fichiers chargés :
            
            1. **Paramètres de Foule** : Ajustez le curseur **Étudiants par profil**. PsychoCrowd va modéliser 4 groupes d'élèves artificiels :
               - **Expert** (≈93% de réussite)
               - **Good** (≈75% de réussite)
               - **Medium** (≈55% de réussite)
               - **Weak** (≈30% de réussite)
               
            2. **Configuration Moteur (API Gemini)** :
               - Cochez **Activer l'API Gemini** pour envoyer les QCM à un grand modèle de langage.
               - Collez votre clé API Gemini (commence par `AIzaSy`).
               - **Note sur la performance** : PsychoCrowd intègre un **système de cache intelligent** dans `data/gemini_cache.json`. La première simulation résout les questions (prend du temps en raison des limites API), mais les lancements suivants sur les mêmes questions sont **instantanés** et ne consomment aucun quota !
               
            3. **Cliquez sur 🚀 LANCER LA SIMULATION**.
            """)

        with step_t[2]:
            st.markdown("""
            ### 📊 Étape 3 : Interprétation du Modèle Psychométrique de Rasch
            Rendez-vous dans les onglets **Foule Synthétique**, **Moteur Rasch** et **Validation** :
            
            1. **Moteur Rasch (Théorie des Réponses aux Items 1PL)** :
               - Ce modèle calcule deux valeurs intrinsèques (en unité *Logit*) :
                 - La **Compétence (θ)** d'un élève (plus sa valeur est haute, plus l'élève est statistiquement fort).
                 - La **Difficulté (b)** d'une question (plus elle est haute, plus la question est complexe).
               
            2. **Carte de Wright** :
               - C'est le graphique de référence. La colonne de gauche représente la distribution des élèves (humains et artificiels), la colonne de droite représente la répartition des questions. Si un élève se situe au même niveau qu'une question, il a exactement **50% de chances de la résoudre**.
               
            3. **Validation Psychométrique** :
               - Permet de mesurer si les étudiants IA se comportent comme les humains. Le **Pearson r** mesure la corrélation linéaire entre les difficultés calculées (un score > 0.85 indique un excellent réalisme).
            """)

        with step_t[3]:
            st.markdown("""
            ### 🔮 Étape 4 : Moteur de Prédictions et Pronostics Individualisés
            Ouvrez l'onglet **Recherche Élève** :
            
            1. **Sélectionnez un élève** (soit un élève humain issu de votre fichier réel, soit un élève synthétique).
            2. **Compétence Latente (θ)** : Le système affiche sa compétence intrinsèque estimée.
            3. **Pronostic par Domaine** : 
               - PsychoCrowd classifie automatiquement les questions du test en sous-domaines (Algèbre, Calcul, Géométrie, Nombres Complexes, Arithmétique).
               - Le moteur applique la formule logistique de Rasch pour **prédire et pronostiquer le taux de réussite futur** de cet élève sur l'ensemble de la banque de questions, y compris celles qu'il n'a pas encore faites !
            4. **Pronostic d'Échecs** :
               - Le système liste les **5 questions précises du test où l'élève est le plus en danger** (les plus faibles probabilités de réussite).
               - Il formule une **recommandation pédagogique sur mesure** pour aider l'enseignant à cibler la remédiation.
            """)

    else:
        # English Guided Tutorial
        st.markdown("""
            <div class='glass-info' style='margin-bottom: 24px;'>
                <p style='margin:0; font-size: 1.05rem; color: #1E293B;'>
                    <b>🎓 Guided Tutorial from A to Z — Mastering PsychoCrowd</b><br>
                    Follow the steps below to unleash the statistical and predictive capabilities of PsychoCrowd.
                </p>
            </div>
        """, unsafe_allow_html=True)

        step_t = st.tabs(["1️⃣ Data Prep", "2️⃣ Simulation settings", "3️⃣ Psychometrics (Rasch)", "4️⃣ Predictions & Forecasting"])

        with step_t[0]:
            st.markdown("""
            ### 📂 Step 1: Prepare and Import CSV Files
            To load custom data, upload two CSV datasets in the sidebar:
            
            1. **MCQ Bank (`mcq_bank.csv`)**:
               - Format: Semicolon `;` or Comma `,` separated.
               - **Headers**: `Question`, `Choice_A` to `Choice_D`, `Correct_Answer` (A/B/C/D), and `Difficulty` (Easy, Medium, Hard).
               
            2. **Human Responses (`human_responses.csv`)**:
               - *Optional.* Allows comparing AI to human students and forecasting their results.
               - **Headers**: `student_id`, `item_id`, and `response` (0=incorrect, 1=correct).
               
            > 💡 **No data?** Keep fields blank! PsychoCrowd will auto-generate mock datasets (1000 math questions, 200 students).
            """)

        with step_t[1]:
            st.markdown("""
            ### 🚀 Step 2: Configure and Launch Simulation
            1. **Crowd Parameters**: Set the number of synthetic students to generate for each profile group (Expert, Good, Medium, Weak).
            2. **Gemini API Configuration**: 
               - Toggle **Enable Google Gemini API** to run questions through an LLM.
               - Paste your Gemini API key.
               - **Performance Tip**: Responses are saved in `data/gemini_cache.json`. The first run solves new items, but subsequent runs are **instantaneous** and consume zero API quota.
            3. **Click 🚀 LAUNCH SIMULATION**.
            """)

        with step_t[2]:
            st.markdown("""
            ### 📊 Step 3: Analyze IRT Rasch Psychometric Model
            Check **Rasch Engine** and **Validation** tabs:
            - **Rasch Model (1PL IRT)**: Estimates student latent **Ability (θ)** and item latent **Difficulty (b)** in Logits.
            - **Wright Map**: Standard representation placing students on the left and items on the right. An aligned student and item means a 50% probability of success.
            - **Validation**: Calculates correlations (Pearson r, Spearman rho, MAE) to show how closely AI students replicate human errors.
            """)

        with step_t[3]:
            st.markdown("""
            ### 🔮 Step 4: Individual Performance Forecasts & Failure Pronostics
            Open the **Student Lookup** tab:
            1. **Select a student** (either a real human or an AI student).
            2. **Latent Ability (θ)**: Displays their estimated capability score.
            3. **Domain-Specific Forecast**: Estimates their future success rate across math areas (Calculus, Algebra, Geometry, Complex Numbers, Arithmetic).
            4. **Failure Alerts**: Flags the **top 5 questions where the student has the highest risk of failing**, providing customized remediation advice.
            """)


# ═══════════════════════════════════════════════════════════════════════
# Pipeline Execution
# ═══════════════════════════════════════════════════════════════════════
if run_btn:
    with st.spinner(T["running_msg"]):
        if mcq_file is not None:
            MCQ_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(MCQ_PATH, "wb") as f:
                f.write(mcq_file.getbuffer())

        if human_file is not None:
            HUMAN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(HUMAN_PATH, "wb") as f:
                f.write(human_file.getbuffer())

        import main as pipeline_module
        api_key_val = api_key if (use_gemini and 'api_key' in locals() and api_key) else None
        report = pipeline_module.run_pipeline(use_gemini=use_gemini, api_key=api_key_val)
        st.balloons()
        st.success(T["success_msg"])
        st.rerun()
