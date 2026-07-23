"""
Centralized CSS styles for the Streamlit application.
"""


def get_custom_css() -> str:
    """
    Returns the complete CSS for dark/light mode compatible styling.

    Returns:
        str: CSS string.
    """
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

        /* ─── Base Styling ─── */
        .stApp {
            background-color: var(--bg);
        }

        /* ─── KPI Cards ─── */
        .kpi-container {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin: 16px 0;
        }

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
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
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

        .kpi-emoji {
            font-size: 1.5rem;
            margin-bottom: 4px;
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
        }

        .personnel-card.risk-expired {
            border-left: 4px solid var(--danger);
        }

        .personnel-card.risk-critical {
            border-left: 4px solid var(--warning);
        }

        .personnel-card.risk-approaching {
            border-left: 4px solid var(--approaching);
        }

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

        .metric-value {
            font-weight: 700;
            font-size: 1.2rem;
            color: var(--text);
        }

        .metric-label {
            font-size: 0.7rem;
            color: var(--text-light);
        }

        /* ─── Responsive ─── */
        @media (max-width: 768px) {
            .kpi-card {
                min-width: 120px;
                padding: 14px 10px;
            }
            .kpi-value {
                font-size: 1.5rem;
            }
            .personnel-card {
                padding: 14px;
            }
        }

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

        /* ─── Tooltip ─── */
        .info-tooltip {
            cursor: help;
            border-bottom: 1px dotted var(--text-light);
        }
    </style>
    """
