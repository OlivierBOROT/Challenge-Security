"""
theme.py — Charte graphique SISE-OPSIE 2026
════════════════════════════════════════════
Thème : "TERMINAL PHOSPHOR" — Esthétique CRT militaire années 80.
Concept : Comme si un analyste SOC pilotait une infrastructure de guerre
          depuis un terminal IBM 3270 overclocked. Monospace omniprésent,
          phosphore vert, scanlines subtiles, glitch sur les titres.

Insertion : importer et appeler inject_theme() en PREMIER dans chaque page,
            juste après st.set_page_config() :

            from src.app.theme import inject_theme
            st.set_page_config(...)   # 1. toujours en premier
            inject_theme()            # 2. juste après
"""

import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# TOKENS DE DESIGN — Modifier ici pour changer toute la charte en une fois
# ══════════════════════════════════════════════════════════════════════════════

# Vert phosphore CRT
PHOSPHOR_GREEN = "#00ff41"  # Couleur signature — titres, bordures actives
PHOSPHOR_DIM = "#00e63a"  # Atténué — texte secondaire (luminosité +15%)
PHOSPHOR_GLOW = "#00ff4133"  # Avec transparence — halos / glow
PHOSPHOR_GHOST = "#00ff4108"  # Quasi-invisible — scanlines

# Fonds
BG_VOID = "#000000"  # Noir absolu — fond principal
BG_SURFACE = "#050f05"  # Très légèrement teinté vert — sidebar
BG_PANEL = "#020a02"  # Fond des cartes / panneaux
BG_HOVER = "#001400"  # Survol des éléments interactifs

# Couleurs sémantiques
DANGER_RED = "#ff2a2a"  # Rouge alerte
WARNING_AMBER = "#ffaa00"  # Ambre — avertissements
INFO_CYAN = "#00d4ff"  # Cyan — informations

# Bordures
BORDER_BRIGHT = "#00ff41"  # Bordures actives
BORDER_DIM = "#0a3d0a"  # Bordures passives
BORDER_MID = "#3a8c3a"  # Bordures moyennes (luminosité augmentée)

# Polices
FONT_MONO = "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"
FONT_DISPLAY = "'Share Tech Mono', 'VT323', monospace"

# ── Couleurs de texte calibrées pour contraste AAA sur fonds sombres ──────────
# Ces valeurs remplacent les anciennes qui étaient illisibles (#1a5c1a, #00c832)
TEXT_BODY = "#d4f5d4"  # Corps de texte — blanc-vert doux, confort lecture
TEXT_LABEL = "#c8f5c8"  # Labels formulaires — fort contraste sur bg-panel
TEXT_SIDEBAR = "#a8e6a8"  # Sidebar — lisible sur #050f05
TEXT_CAPTION = "#6abf6a"  # Captions / muted — ratio ≥ 4.5:1 sur noir
TEXT_INPUT = "#e8ffe8"  # Valeurs dans inputs / selectbox
TEXT_MUTED = "#4a9e4a"  # Très secondaire (disabled, placeholders)


def inject_theme() -> None:
    """
    Injecte l'intégralité de la charte graphique via st.markdown.

    À appeler UNE SEULE FOIS par page, juste après st.set_page_config().
    Couvre : polices, reset global, sidebar, labels, métriques, boutons,
             alertes, dataframes, inputs, composants custom, scrollbar.
    """
    st.markdown(
        f"""
    <style>
    /* ═══════════════════════════════════════════════════════════════════════
       POLICES GOOGLE FONTS
       JetBrains Mono  → corps de texte, code, labels
       Share Tech Mono → titres, valeurs KPI, style terminal
    ═══════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Share+Tech+Mono&display=swap');
    /* Material Icons (restore Streamlit icons when global font is overridden) */
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Outlined|Material+Icons+Round|Material+Icons+Sharp|Material+Icons+Two+Tone');

    /* Ensure material icon glyphs render correctly despite global monospace */
    .material-icons,
    .material-icons-outlined,
    .material-icons-round,
    .material-icons-sharp,
    .material-icons-two-tone {{
        font-family: 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: inherit !important;
        line-height: 1 !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       VARIABLES CSS GLOBALES
    ═══════════════════════════════════════════════════════════════════════ */
    :root {{
        --phosphor:      {PHOSPHOR_GREEN};
        --phosphor-dim:  {PHOSPHOR_DIM};
        --phosphor-glow: {PHOSPHOR_GLOW};
        --bg-void:       {BG_VOID};
        --bg-surface:    {BG_SURFACE};
        --bg-panel:      {BG_PANEL};
        --danger:        {DANGER_RED};
        --warning:       {WARNING_AMBER};
        --info:          {INFO_CYAN};
        --border-bright: {BORDER_BRIGHT};
        --border-dim:    {BORDER_DIM};
        --border-mid:    {BORDER_MID};
        --font-mono:     {FONT_MONO};
        --font-display:  {FONT_DISPLAY};
        --text-body:     {TEXT_BODY};
        --text-label:    {TEXT_LABEL};
        --text-sidebar:  {TEXT_SIDEBAR};
        --text-caption:  {TEXT_CAPTION};
        --text-input:    {TEXT_INPUT};
        --glow-sm: 0 0 8px {PHOSPHOR_GLOW};
        --glow-md: 0 0 20px {PHOSPHOR_GLOW}, 0 0 40px {PHOSPHOR_GHOST};
        --glow-lg: 0 0 40px {PHOSPHOR_GLOW}, 0 0 80px {PHOSPHOR_GHOST};
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       RESET GLOBAL + FOND PRINCIPAL
    ═══════════════════════════════════════════════════════════════════════ */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {{
        background-color: var(--bg-void) !important;
        color: var(--text-body) !important;
        font-family: var(--font-mono) !important;
    }}

    /* Scanlines CRT animées — overlay fixe sur tout l'écran */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: repeating-linear-gradient(
            0deg,
            transparent, transparent 2px,
            {PHOSPHOR_GHOST} 2px, {PHOSPHOR_GHOST} 4px
        );
        pointer-events: none;
        z-index: 9999;
        animation: scanlines 8s linear infinite;
    }}
    @keyframes scanlines {{
        0%   {{ background-position: 0 0; }}
        100% {{ background-position: 0 100vh; }}
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       TEXTE COURANT — Paragraphes, listes, markdown
       FIX : sans ce bloc, les <p> héritaient de la couleur Streamlit (gris)
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    p, li {{
        color: var(--text-body) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        line-height: 1.7 !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       TITRES — Effet glitch phosphore sur h1
    ═══════════════════════════════════════════════════════════════════════ */
    h1, h2, h3, h4 {{
        font-family: var(--font-display) !important;
        color: var(--phosphor) !important;
        letter-spacing: 0.06em !important;
        text-shadow: var(--glow-sm) !important;
    }}

    h1 {{
        font-size: 1.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        text-shadow: var(--glow-md) !important;
        animation: glitch-title 6s infinite !important;
    }}
    @keyframes glitch-title {{
        0%, 92%, 100% {{
            text-shadow: var(--glow-md);
            transform: translate(0);
        }}
        93% {{
            text-shadow: 2px 0 {DANGER_RED}, -2px 0 {INFO_CYAN}, var(--glow-md);
            transform: translate(-1px, 0);
        }}
        94% {{
            text-shadow: -2px 0 {DANGER_RED}, 2px 0 {INFO_CYAN}, var(--glow-md);
            transform: translate(1px, 0);
        }}
        95% {{ text-shadow: var(--glow-md); transform: translate(0); }}
    }}

    h2 {{
        font-size: 1.15rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border-bottom: 1px solid var(--border-mid) !important;
        padding-bottom: 6px !important;
        margin-top: 1.5rem !important;
    }}

    h3 {{
        font-size: 0.95rem !important;
        letter-spacing: 0.08em !important;
        color: var(--phosphor-dim) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {{
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border-mid) !important;
        box-shadow: 4px 0 30px {PHOSPHOR_GHOST} !important;
    }}

    /* FIX : ancien #00c832 illisible sur #050f05 → remplacé par #a8e6a8 */
    [data-testid="stSidebar"] * {{
        font-family: var(--font-mono) !important;
        color: var(--text-sidebar) !important;
    }}

    /* Hide Streamlit sidebar collapse arrow (top icon) — not needed for this UI */
    [data-testid="stSidebar"] span[data-testid="stIconMaterial"]:first-of-type {{
        display: none !important;
    }}

    /* Liens de navigation (noms des pages) */
    [data-testid="stSidebarNavLink"] span,
    [data-testid="stSidebarNav"] a {{
        color: var(--text-sidebar) !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.05em !important;
        transition: color 0.15s !important;
    }}
    [data-testid="stSidebarNavLink"]:hover span,
    [data-testid="stSidebarNavLink"][aria-current="page"] span {{
        color: var(--phosphor) !important;
        text-shadow: var(--glow-sm) !important;
    }}

    /* Boutons dans la sidebar */
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        border: 1px solid var(--border-mid) !important;
        color: var(--text-sidebar) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border-radius: 2px !important;
        transition: all 0.15s !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: var(--phosphor) !important;
        color: var(--phosphor) !important;
        box-shadow: var(--glow-sm) !important;
        background: {BG_HOVER} !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       LABELS DE FORMULAIRES
       FIX : sans ciblage explicite, Streamlit impose sa couleur grise native
             qui est illisible sur nos fonds sombres
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    label[data-testid="stWidgetLabel"],
    .stSelectbox label,
    .stSlider label,
    .stCheckbox label,
    .stNumberInput label,
    .stDateInput label,
    .stTextInput label,
    div[data-testid="stFormLabel"] p {{
        color: var(--text-label) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        opacity: 1 !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       CAPTIONS / TEXTE SECONDAIRE
       FIX : ancien BORDER_MID = #1a5c1a quasi invisible → #6abf6a (ratio 4.5:1)
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"],
    .stCaption, small {{
        color: var(--text-caption) !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em !important;
        font-family: var(--font-mono) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       MÉTRIQUES KPI
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="metric-container"] {{
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: 3px !important;
        padding: 14px 18px !important;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }}
    /* Barre phosphore à gauche */
    [data-testid="metric-container"]::before {{
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: var(--phosphor);
        box-shadow: var(--glow-sm);
    }}
    [data-testid="metric-container"]:hover {{
        border-color: var(--phosphor) !important;
        box-shadow: var(--glow-sm) !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: var(--font-display) !important;
        color: var(--phosphor) !important;
        font-size: 2rem !important;
        text-shadow: var(--glow-sm) !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-family: var(--font-mono) !important;
        color: var(--text-caption) !important;
        font-size: 0.68rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       DATAFRAMES / TABLEAUX
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border-mid) !important;
        border-radius: 2px !important;
    }}
    [data-testid="stDataFrame"] th {{
        background: var(--bg-panel) !important;
        color: var(--phosphor) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border-bottom: 1px solid var(--border-mid) !important;
        padding: 8px 12px !important;
    }}
    [data-testid="stDataFrame"] td {{
        background: var(--bg-surface) !important;
        color: var(--text-body) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.82rem !important;
        border-bottom: 1px solid var(--border-dim) !important;
    }}
    [data-testid="stDataFrame"] tr:hover td {{
        background: {BG_HOVER} !important;
        color: var(--phosphor) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       BOUTONS
    ═══════════════════════════════════════════════════════════════════════ */
    .stButton > button {{
        background: transparent !important;
        border: 1px solid var(--border-bright) !important;
        color: var(--phosphor) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        border-radius: 2px !important;
        padding: 8px 20px !important;
        transition: all 0.15s ease !important;
    }}
    .stButton > button:hover {{
        box-shadow: var(--glow-md) !important;
        background: {BG_HOVER} !important;
    }}
    .stButton > button:active  {{ transform: scale(0.98) !important; }}
    .stButton > button:disabled {{
        border-color: var(--border-dim) !important;
        color: {TEXT_MUTED} !important;
        box-shadow: none !important;
    }}

    /* Download button */
    [data-testid="stDownloadButton"] button {{
        background: transparent !important;
        border: 1px solid var(--border-mid) !important;
        color: var(--text-label) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.08em !important;
        border-radius: 2px !important;
        transition: all 0.15s !important;
    }}
    [data-testid="stDownloadButton"] button:hover {{
        border-color: var(--phosphor) !important;
        color: var(--phosphor) !important;
        box-shadow: var(--glow-sm) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       FORMULAIRES — Sliders, Selects, Inputs
       FIX : valeurs affichées en --text-input (#e8ffe8), lisible sur bg-panel
    ═══════════════════════════════════════════════════════════════════════ */

    /* Slider — piste et poignée */
    [data-testid="stSlider"] > div > div > div {{
        background: var(--phosphor) !important;
        box-shadow: var(--glow-sm) !important;
    }}
    /* Valeurs min/max et courante du slider */
    [data-testid="stSlider"] p,
    [data-testid="stSlider"] [data-testid="stTickBar"],
    [data-testid="stSlider"] [data-testid="stThumbValue"] {{
        color: var(--text-caption) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
    }}

    /* Selectbox */
    .stSelectbox > div > div,
    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {{
        background: var(--bg-panel) !important;
        border-color: var(--border-mid) !important;
        color: var(--text-input) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        border-radius: 2px !important;
    }}

    /* Number input & text input */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {{
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-mid) !important;
        color: var(--text-input) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        border-radius: 2px !important;
    }}

    /* Focus sur tous les inputs */
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {{
        border-color: var(--phosphor) !important;
        box-shadow: var(--glow-sm) !important;
        outline: none !important;
    }}

    /* Checkbox */
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] label p {{
        color: var(--text-label) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.04em !important;
    }}

    /* Options du dropdown selectbox */
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [role="option"] {{
        background: var(--bg-panel) !important;
        color: var(--text-body) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.82rem !important;
    }}
    [data-baseweb="popover"] li:hover,
    [role="option"]:hover {{
        background: {BG_HOVER} !important;
        color: var(--phosphor) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       ALERTES / MESSAGES STREAMLIT
    ═══════════════════════════════════════════════════════════════════════ */
    div[data-testid="stSuccessMessage"],
    div[data-testid="stSuccessMessage"] p {{
        background: rgba(0, 255, 65, 0.05) !important;
        border-color: var(--phosphor) !important;
        color: var(--phosphor) !important;
        font-family: var(--font-mono) !important;
    }}
    div[data-testid="stErrorMessage"],
    div[data-testid="stErrorMessage"] p {{
        background: rgba(255, 42, 42, 0.06) !important;
        border-color: var(--danger) !important;
        color: var(--danger) !important;
        font-family: var(--font-mono) !important;
        animation: pulse-danger 2s ease-in-out infinite !important;
    }}
    @keyframes pulse-danger {{
        0%, 100% {{ box-shadow: 0 0 8px rgba(255, 42, 42, 0.2); }}
        50%       {{ box-shadow: 0 0 20px rgba(255, 42, 42, 0.4); }}
    }}
    div[data-testid="stWarningMessage"],
    div[data-testid="stWarningMessage"] p {{
        background: rgba(255, 170, 0, 0.05) !important;
        border-color: var(--warning) !important;
        color: var(--warning) !important;
        font-family: var(--font-mono) !important;
    }}
    div[data-testid="stInfoMessage"],
    div[data-testid="stInfoMessage"] p {{
        background: rgba(0, 212, 255, 0.04) !important;
        border-color: var(--info) !important;
        color: var(--info) !important;
        font-family: var(--font-mono) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       EXPANDER
    ═══════════════════════════════════════════════════════════════════════ */
    details {{
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        border-radius: 2px !important;
    }}
    details summary {{
        color: var(--text-label) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.05em !important;
        padding: 8px 12px !important;
        cursor: pointer !important;
    }}
    details summary:hover,
    details[open] summary {{ color: var(--phosphor) !important; }}
    details[open] summary {{
        border-bottom: 1px solid var(--border-dim) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       DIVIDERS
    ═══════════════════════════════════════════════════════════════════════ */
    hr {{
        border: none !important;
        border-top: 1px solid var(--border-dim) !important;
        margin: 1.5rem 0 !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       PLOTLY CHARTS
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stPlotlyChart"] {{
        border: 1px solid var(--border-dim) !important;
        border-radius: 2px !important;
        background: var(--bg-panel) !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       PROGRESS BAR
    ═══════════════════════════════════════════════════════════════════════ */
    [data-testid="stProgress"] > div > div {{
        background: var(--bg-panel) !important;
        border-radius: 1px !important;
    }}
    [data-testid="stProgress"] > div > div > div {{
        background: linear-gradient(90deg, var(--phosphor-dim), var(--phosphor)) !important;
        box-shadow: var(--glow-sm) !important;
        border-radius: 1px !important;
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       SCROLLBAR
    ═══════════════════════════════════════════════════════════════════════ */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-void); }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-mid);
        border-radius: 1px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--phosphor-dim);
        box-shadow: var(--glow-sm);
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       SÉLECTION DE TEXTE
    ═══════════════════════════════════════════════════════════════════════ */
    ::selection {{
        background: {PHOSPHOR_GLOW};
        color: var(--phosphor);
    }}

    /* ═══════════════════════════════════════════════════════════════════════
       COMPOSANTS CUSTOM HTML
       Usage : st.markdown(soc_card("texte", "danger"), unsafe_allow_html=True)
    ═══════════════════════════════════════════════════════════════════════ */

    /* Carte SOC */
    .soc-card {{
        background: var(--bg-panel);
        border: 1px solid var(--border-dim);
        border-left: 3px solid var(--phosphor);
        border-radius: 2px;
        padding: 16px 20px;
        margin: 10px 0;
        font-family: var(--font-mono);
        color: var(--text-body);
        transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .soc-card:hover {{ box-shadow: var(--glow-sm); }}
    .soc-card.danger  {{ border-left-color: var(--danger);  background: rgba(255,42,42,0.04);  color: {
            DANGER_RED
        }; }}
    .soc-card.warning {{ border-left-color: var(--warning); background: rgba(255,170,0,0.04);  color: {
            WARNING_AMBER
        }; }}
    .soc-card.info    {{ border-left-color: var(--info);    background: rgba(0,212,255,0.04);  color: {
            INFO_CYAN
        }; }}

    /* Badge terminal inline */
    .terminal-badge {{
        display: inline-block;
        padding: 2px 8px;
        border: 1px solid var(--border-mid);
        border-radius: 1px;
        font-size: 0.68rem;
        font-family: var(--font-mono);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-label);
        background: var(--bg-panel);
    }}
    .terminal-badge.active {{
        border-color: var(--phosphor);
        color: var(--phosphor);
        box-shadow: var(--glow-sm);
        animation: blink-cursor 1.2s step-end infinite;
    }}
    .terminal-badge.danger {{ border-color: var(--danger); color: var(--danger); }}
    @keyframes blink-cursor {{
        0%, 100% {{ opacity: 1; }}
        50%       {{ opacity: 0.4; }}
    }}

    /* Indicateur de niveau de menace */
    .threat-level {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: var(--font-mono);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-body);
    }}
    .threat-level .dot {{
        width: 8px; height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }}
    .threat-level.critical .dot {{ background: var(--danger);   box-shadow: 0 0 8px var(--danger);   animation: pulse-danger 1s infinite; }}
    .threat-level.high     .dot {{ background: var(--warning);  box-shadow: 0 0 8px var(--warning); }}
    .threat-level.medium   .dot {{ background: var(--info);     box-shadow: 0 0 8px var(--info); }}
    .threat-level.low      .dot {{ background: var(--phosphor); box-shadow: var(--glow-sm); }}

    /* Ligne clé / valeur */
    .data-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid var(--border-dim);
        font-family: var(--font-mono);
        font-size: 0.82rem;
        color: var(--text-body);
    }}
    .data-row:last-child {{ border-bottom: none; }}
    .data-row .key   {{ color: var(--text-caption); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }}
    .data-row .value {{ color: var(--phosphor); font-weight: 500; }}
    .data-row .value.red   {{ color: var(--danger);  }}
    .data-row .value.amber {{ color: var(--warning); }}
    .data-row .value.cyan  {{ color: var(--info); }}

    /* Header de section */
    .section-header {{
        font-family: var(--font-display);
        font-size: 0.78rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--text-caption);
        border-bottom: 1px solid var(--border-dim);
        padding-bottom: 6px;
        margin: 20px 0 14px 0;
    }}
    .section-header::before {{
        content: "//  ";
        color: var(--phosphor);
        opacity: 0.6;
    }}

    /* KPI Card — unified style for dashboard metric boxes */
    .kpi-card {{
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
        color: var(--text-body) !important;
        font-family: var(--font-mono) !important;
        box-shadow: 0 4px 18px var(--phosphor-ghost, rgba(0,255,65,0.04)) !important;
        transition: border-color 0.18s, box-shadow 0.18s !important;
        display: block;
    }}
    .kpi-card:hover {{
        border - color: var(--phosphor) !important;
        box-shadow: var(--glow-sm) !important;
    }}
    .kpi-card .kpi-label {{
        color: var(--text-caption) !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }}
    .kpi-card .kpi-value {{
        color: var(--phosphor) !important;
        font-family: var(--font-display) !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        margin-top: 6px !important;
        text-shadow: var(--glow-sm) !important;
    }}
    .kpi-card .kpi-sub {{
        color: var(--text-caption) !important;
        font-size: 0.72rem !important;
        margin-top: 6px !important;
    }}

    /* Map legends (color & size) */
    .map-legend {{ display:block; }}
    .map-legend .legend-box {{
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-dim) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        color: var(--text-body) !important;
        font-family: var(--font-mono) !important;
        max-height: 360px !important;
        overflow-y: auto !important;
    }}
    .map-legend .legend-title {{
        font-size: 0.85rem !important;
        color: var(--text-caption) !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
    }}
    .map-legend .legend-item {{ display:flex; align-items:center; gap:8px; margin:4px 0; }}
    .map-legend .legend-swatch {{ width:12px; height:12px; border-radius:2px; border:1px solid var(--border-dim); flex-shrink:0; }}
    .map-legend .legend-label {{ font-size:0.88rem; color:var(--text-body); white-space:nowrap; }}
    .map-legend .legend-gradient {{ width:18px; border-radius:4px; border:1px solid var(--border-dim); flex-shrink:0; }}
    .map-legend .legend-gradient-values {{ display:flex; flex-direction:column; justify-content:space-between; margin-left:8px; font-size:11px; color:var(--text-body); }}
    .map-legend .legend-circle {{ flex-shrink:0; }}

    </style>
    """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# COMPOSANTS HTML RÉUTILISABLES
# ══════════════════════════════════════════════════════════════════════════════


def soc_card(content: str, variant: str = "") -> str:
    """Carte SOC colorée. variant : 'danger' | 'warning' | 'info' | ''"""
    return f'<div class="soc-card {variant}">{content}</div>'


def terminal_badge(text: str, variant: str = "") -> str:
    """Badge inline terminal. variant : 'active' | 'danger' | ''"""
    return f'<span class="terminal-badge {variant}">{text}</span>'


def threat_level(level: str, label: str) -> str:
    """Point lumineux + label de menace. level : 'critical' | 'high' | 'medium' | 'low'"""
    return f"""<div class="threat-level {level}">
        <div class="dot"></div><span>{label}</span>
    </div>"""


def section_header(title: str) -> str:
    """En-tête de section avec préfixe // style terminal."""
    return f'<div class="section-header">{title}</div>'


def data_row(key: str, value: str, value_class: str = "") -> str:
    """Ligne clé/valeur. value_class : 'red' | 'amber' | 'cyan' | ''"""
    return f"""<div class="data-row">
        <span class="key">{key}</span>
        <span class="value {value_class}">{value}</span>
    </div>"""
