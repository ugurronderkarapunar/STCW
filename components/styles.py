"""
Centralized CSS styles for the Streamlit application.
Includes base styles, light theme, dark theme, animations, and loading effects.
"""

def get_custom_css() -> str:
    """Base styles with CSS variables and animations."""
    return """
    <style>
        /* ─── Root Variables ─── */
        :root {
            --primary: #1B3A5C;
            --primary-light: #2C5F8A;
            --accent: #E8913A;
            --bg: #F5F7FA;
            --card-bg: #FFFFFF;
            --text: #2C3E50;
            --text-light: #7F8C8D;
            --danger: #FF4136;
            --warning: #FF851B;
            --approaching: #FFDC00;
            --success: #2ECC40;
            --no-date: #AAAAAA;
            --border: #E1E8ED;
            --shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        /* ─── Animations ─── */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 65, 54, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 65, 54, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 65, 54, 0); }
        }
        @keyframes skeleton-loading {
            0% { background-position: -200px 0; }
            100% { background-position: calc(200px + 100%) 0; }
        }
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out forwards;
        }
        .animate-slide-in {
            animation: slideInLeft 0.4s ease-out forwards;
        }
        .animate-pulse {
            animation: pulse 2s infinite;
        }
        .skeleton {
            background: linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%);
            background-size: 200px 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 8px;
            height: 20px;
        }

        /* ─── Base Styling ─── */
        .stApp {
            background-color: var(--bg);
        }

        /* ─── Logo & Header ─── */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            padding: 16px 0;
        }
        .app-logo {
            width: 64px;
            height: 64px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
        .app-title {
            color: var(--primary);
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }
        .company-name {
            color: var(--text-light);
            font-size: 1rem;
            margin-top: 4px;
        }

        /* ─── KPI Cards ─── */
        .kpi-card {
            flex: 1;
            min-width: 140px;
            padding: 20px 16px;
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            text-align: center;
            border-left: 4px solid var(--primary);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            animation: fadeIn 0.6s ease-out;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }
        .kpi-card.danger { border-left-color: var(--danger); }
        .kpi-card.warning { border-left-color: var(--warning); }
        .kpi-card.approaching { border-left-color: var(--approaching); }
        .kpi-card.success { border-left-color: var(--success); }
        .kpi-card.no-date { border-left-color: var(--no-date); }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text);
            line-height: 1.2;
        }
        .kpi-label {
            font-size: 0.85rem;
            color: var(--text-light);
            margin-top: 4px;
            font-weight: 500;
        }

        /* ─── Status Badges ─── */
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #FFFFFF;
            text-align: center;
            white-space: nowrap;
        }
        .status-expired { background-color: var(--danger); }
        .status-critical { background-color: var(--warning); }
        .status-approaching { background-color: #D4A000; }
        .status-valid { background-color: var(--success); }
        .status-no-date { background-color: var(--no-date); }

        /* ─── Personnel Card ─── */
        .personnel-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin: 12px 0;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            animation: slideInLeft 0.4s ease-out;
        }
        .personnel-card.risk-expired { border-left: 4px solid var(--danger); }
        .personnel-card.risk-critical { border-left: 4px solid var(--warning); }
        .personnel-card.risk-approaching { border-left: 4px solid var(--approaching); }
        .personnel-name {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text);
        }
        .personnel-rank {
            font-size: 0.85rem;
            color: var(--text-light);
            margin-bottom: 8px;
        }
        .document-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }
        .document-tag {
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #FFFFFF;
        }
        .tag-expired { background-color: var(--danger); }
        .tag-critical { background-color: var(--warning); }
        .tag-approaching { background-color: #D4A000; }

        /* ─── Section Headers ─── */
        .section-header {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--primary);
            margin: 24px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--primary-light);
        }

        /* ─── Metric Row ─── */
        .metric-row {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 8px 0;
        }
        .metric-item {
            text-align: center;
            padding: 8px 16px;
            background: #f8f9fa;
            border-radius: 8px;
            min-width: 80px;
        }
        .metric-value { font-weight: 700; font-size: 1.2rem; color: var(--text); }
        .metric-label { font-size: 0.7rem; color: var(--text-light); }

        /* ─── Download Button ─── */
        .download-section {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 16px 0;
        }

        /* ─── Alert Box ─── */
        .alert-box {
            padding: 16px;
            border-radius: 8px;
            margin: 12px 0;
            font-weight: 500;
            animation: fadeIn 0.5s ease-out;
        }
        .alert-error {
            background-color: #FDEDEC;
            border: 1px solid #E74C3C;
            color: #C0392B;
        }
        .alert-warning {
            background-color: #FEF9E7;
            border: 1px solid #F39C12;
            color: #B7950B;
        }
        .alert-success {
            background-color: #EAFAF1;
            border: 1px solid #27AE60;
            color: #1E8449;
        }

        /* ─── Refresh Button Animation ─── */
        .refresh-btn {
            transition: transform 0.3s ease;
        }
        .refresh-btn:hover {
            transform: rotate(180deg);
        }

        @media (max-width: 768px) {
            .kpi-card { min-width: 120px; padding: 14px 10px; }
            .kpi-value { font-size: 1.5rem; }
            .personnel-card { padding: 14px; }
        }
    </style>
    """

def get_light_theme_css() -> str:
    return """
    <style>
        :root {
            --bg: #F5F7FA;
            --card-bg: #FFFFFF;
            --text: #2C3E50;
            --text-light: #7F8C8D;
            --border: #E1E8ED;
            --shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            --primary: #1B3A5C;
            --primary-light: #2C5F8A;
        }
        .stApp { background-color: var(--bg); }
        .metric-item { background: #f8f9fa; }
    </style>
    """

def get_dark_theme_css() -> str:
    return """
    <style>
        :root {
            --bg: #0f1923;
            --card-bg: #1a2d3d;
            --text: #e2e8f0;
            --text-light: #94a3b8;
            --border: #2d4a5e;
            --shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
            --primary: #60a5fa;
            --primary-light: #93c5fd;
        }
        .stApp { background-color: var(--bg); }
        .kpi-card, .personnel-card, .alert-box {
            background-color: var(--card-bg);
            color: var(--text);
            box-shadow: var(--shadow);
        }
        .kpi-value, .personnel-name { color: var(--text); }
        .kpi-label, .personnel-rank, .metric-label { color: var(--text-light); }
        .section-header { color: #60a5fa; border-bottom-color: #60a5fa; }
        .metric-item { background: #1e3a4d; }
        .metric-value { color: var(--text); }
        [data-testid="stSidebar"] { background-color: #0d1b26; }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        .stTextInput input, .stSelectbox select, .stMultiSelect div {
            background-color: #1a2d3d !important;
            color: #e2e8f0 !important;
            border-color: #2d4a5e !important;
        }
    </style>
    """
