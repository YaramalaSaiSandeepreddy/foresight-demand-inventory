import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="FORESIGHT",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 88% 3%, #dbeafe 0%, transparent 22%),
                linear-gradient(135deg, #f8fbff 0%, #f3f7fc 100%);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #081b33 0%, #102f56 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }

        [data-testid="stSidebar"] .stRadio label {
            padding: 7px 4px;
            font-size: 16px;
        }

        .hero {
            padding: 28px 32px;
            margin-bottom: 26px;
            border-radius: 22px;
            color: white;
            background:
                radial-gradient(circle at 85% 10%, rgba(96, 165, 250, .70), transparent 28%),
                linear-gradient(115deg, #071b33 0%, #0f4c81 58%, #2563eb 100%);
            box-shadow: 0 16px 35px rgba(15, 76, 129, 0.20);
        }

        .hero-title {
            margin: 0;
            font-size: 42px;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .hero-subtitle {
            margin-top: 8px;
            font-size: 17px;
            opacity: .88;
        }

        .section-title {
            margin: 12px 0 14px 0;
            color: #102a43;
            font-size: 24px;
            font-weight: 750;
        }

        .kpi-card {
            min-height: 122px;
            padding: 19px 20px;
            margin-bottom: 18px;
            border-radius: 18px;
            background: rgba(255, 255, 255, .92);
            border: 1px solid rgba(203, 213, 225, .85);
            box-shadow: 0 8px 20px rgba(15, 23, 42, .07);
        }

        .kpi-label {
            color: #64748b;
            font-size: 14px;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: .5px;
        }

        .kpi-value {
            margin-top: 10px;
            color: #102a43;
            font-size: 30px;
            font-weight: 800;
            line-height: 1.05;
        }

        .kpi-blue { border-left: 6px solid #2563eb; }
        .kpi-green { border-left: 6px solid #16a34a; }
        .kpi-red { border-left: 6px solid #dc2626; }
        .kpi-orange { border-left: 6px solid #f97316; }
        .kpi-purple { border-left: 6px solid #7c3aed; }
        .kpi-teal { border-left: 6px solid #0f766e; }

        .insight-box {
            padding: 20px 22px;
            margin-bottom: 15px;
            border-radius: 16px;
            background: white;
            border-left: 5px solid #2563eb;
            box-shadow: 0 7px 18px rgba(15, 23, 42, .06);
            color: #1e293b;
        }

        div[data-testid="stDataFrame"] {
            background: white;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #dbe4ef;
        }

        .stSelectbox label {
            color: #334e68 !important;
            font-weight: 700 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    weekly = pd.read_csv(
        ROOT / "data/processed/weekly_demand.csv",
        parse_dates=["week"],
    )
    forecast = pd.read_csv(
        ROOT / "outputs/forecast.csv",
        parse_dates=["forecast_week"],
    )
    risk = pd.read_csv(ROOT / "outputs/risk_scores.csv")
    results = pd.read_csv(ROOT / "reports/model_results.csv")
    sku_master = pd.read_csv(ROOT / "data/processed/sku_master.csv")

    return weekly, forecast, risk, results, sku_master


def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, color="blue"):
    st.markdown(
        f"""
        <div class="kpi-card kpi-{color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_style(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", color="#334e68"),
        title_font=dict(size=21, color="#102a43"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        margin=dict(l=25, r=25, t=65, b=25),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#e2e8f0", linecolor="#cbd5e1")
    return fig


weekly, fc, risk, results, sku = load_data()
model_info = joblib.load(ROOT / "models/forecast_model.joblib")

st.sidebar.markdown("## 📈 FORESIGHT")
st.sidebar.caption("Demand & Inventory Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Forecast", "Risk", "Decision Grid", "Insights"],
)

st.sidebar.markdown("---")
st.sidebar.caption("NorthBay Living • Decision Support")


if page == "Overview":
    hero(
        "FORESIGHT",
        "Demand & Inventory Intelligence for NorthBay Living",
    )

    total_revenue = weekly["revenue"].sum()
    total_units = weekly["demand"].sum()
    total_skus = weekly["sku_id"].nunique()

    reorder_count = (risk["recommended_action"] == "REORDER NOW").sum()
    markdown_count = (risk["recommended_action"] == "MARKDOWN / CLEAR").sum()
    healthy_count = (risk["recommended_action"] == "HEALTHY").sum()

    st.markdown('<div class="section-title">Business Overview</div>', unsafe_allow_html=True)

    row_1 = st.columns(3)
    with row_1[0]:
        kpi_card("Total SKUs", f"{total_skus:,}", "blue")
    with row_1[1]:
        kpi_card("Total Revenue", f"{total_revenue:,.0f}", "purple")
    with row_1[2]:
        kpi_card("Total Units Sold", f"{total_units:,.0f}", "teal")

    row_2 = st.columns(3)
    with row_2[0]:
        kpi_card("Reorder Now", f"{reorder_count:,}", "red")
    with row_2[1]:
        kpi_card("Markdown / Clear", f"{markdown_count:,}", "orange")
    with row_2[2]:
        kpi_card("Healthy SKUs", f"{healthy_count:,}", "green")

    st.markdown('<div class="section-title">Estimated Business Impact</div>', unsafe_allow_html=True)

    impact_left, impact_right = st.columns(2)
    with impact_left:
        kpi_card(
            "Estimated Sales at Risk",
            f"{risk['sales_at_risk'].sum():,.0f}",
            "red",
        )
    with impact_right:
        kpi_card(
            "Estimated Capital Locked",
            f"{risk['capital_locked'].sum():,.0f}",
            "orange",
        )

    weekly_total = (
        weekly.groupby("week", as_index=False)["demand"]
        .sum()
        .sort_values("week")
    )

    demand_chart = px.line(
        weekly_total,
        x="week",
        y="demand",
        title="Total Weekly Demand Trend",
        labels={"week": "Week", "demand": "Units Sold"},
    )
    demand_chart.update_traces(
        line=dict(color="#2563eb", width=3),
        fill="tozeroy",
        fillcolor="rgba(37, 99, 235, 0.10)",
    )

    st.plotly_chart(chart_style(demand_chart), use_container_width=True)

    st.caption(
        "Sales at risk and capital locked are estimates based on the supplied "
        "inventory snapshot, forecast demand, SKU price/cost, and a documented "
        "two-week lead-time assumption."
    )


elif page == "Forecast":
    hero(
        "Demand Forecast",
        "Explore historical weekly demand and the eight-week SKU forecast.",
    )

    selected_sku = st.selectbox(
        "Select a SKU",
        sorted(weekly["sku_id"].unique()),
    )

    history = weekly[weekly["sku_id"] == selected_sku]
    future = fc[fc["sku_id"] == selected_sku]

    forecast_chart = px.line(
        history,
        x="week",
        y="demand",
        title=f"{selected_sku} — Historical Demand and Future Forecast",
        labels={"week": "Week", "demand": "Demand"},
    )

    forecast_chart.update_traces(
        line=dict(color="#2563eb", width=3),
        name="Historical Demand",
    )

    forecast_chart.add_scatter(
        x=future["forecast_week"],
        y=future["forecast_demand"],
        mode="lines+markers",
        name="8-Week Forecast",
        line=dict(color="#f97316", width=3, dash="dash"),
        marker=dict(size=8),
    )

    st.plotly_chart(chart_style(forecast_chart), use_container_width=True)

    st.markdown(
        '<div class="section-title">Time-Based Model Validation</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        results.style.format(
            {
                "wape": "{:.2%}",
                "mae": "{:.2f}",
                "rmse": "{:.2f}",
                "bias": "{:.2%}",
            }
        ),
        use_container_width=True,
    )

    if model_info["selected_model"] == "ml":
        selected_model_name = "HistGradientBoostingRegressor"
    else:
        selected_model_name = "Seasonal Naive (8-Week Lag)"

    st.markdown(
        f"""
        <div class="insight-box">
            <b>Selected production method:</b> {selected_model_name}<br>
            The model selection is based on the lower validation WAPE.
        </div>
        """,
        unsafe_allow_html=True,
    )


elif page == "Risk":
    hero(
        "Inventory Risk Center",
        "Prioritise reorder decisions, markdown opportunities, and healthy inventory.",
    )

    filter_left, filter_right = st.columns(2)

    with filter_left:
        category = st.selectbox(
            "Filter by Category",
            ["All"] + sorted(risk["category"].dropna().unique().tolist()),
        )

    with filter_right:
        action = st.selectbox(
            "Filter by Recommended Action",
            ["All"] + sorted(risk["recommended_action"].unique().tolist()),
        )

    view = risk.copy()

    if category != "All":
        view = view[view["category"] == category]

    if action != "All":
        view = view[view["recommended_action"] == action]

    reorder_count = (view["recommended_action"] == "REORDER NOW").sum()
    markdown_count = (view["recommended_action"] == "MARKDOWN / CLEAR").sum()
    healthy_count = (view["recommended_action"] == "HEALTHY").sum()

    count_row = st.columns(3)
    with count_row[0]:
        kpi_card("Reorder Now", f"{reorder_count:,}", "red")
    with count_row[1]:
        kpi_card("Markdown / Clear", f"{markdown_count:,}", "orange")
    with count_row[2]:
        kpi_card("Healthy", f"{healthy_count:,}", "green")

    st.markdown(
        '<div class="section-title">SKU-Level Risk Recommendations</div>',
        unsafe_allow_html=True,
    )

    display_columns = [
        "sku_id",
        "category",
        "forecast_demand",
        "stockout_risk",
        "overstock_risk",
        "risk_level",
        "recommended_action",
        "sales_at_risk",
        "capital_locked",
    ]

    st.dataframe(
        view[display_columns].style.format(
            {
                "forecast_demand": "{:.1f}",
                "stockout_risk": "{:.2%}",
                "overstock_risk": "{:.2%}",
                "sales_at_risk": "{:,.0f}",
                "capital_locked": "{:,.0f}",
            }
        ),
        use_container_width=True,
        height=520,
    )


elif page == "Decision Grid":
    hero(
        "Decision Grid",
        "Use stockout and overstock risk together to prioritise inventory actions.",
    )

    decision_grid = px.scatter(
        risk,
        x="overstock_risk",
        y="stockout_risk",
        color="recommended_action",
        hover_data=["sku_id", "forecast_demand", "category"],
        title="Inventory Decision Grid",
        labels={
            "overstock_risk": "Overstock Risk",
            "stockout_risk": "Stockout Risk",
            "recommended_action": "Recommended Action",
        },
        color_discrete_map={
            "REORDER NOW": "#dc2626",
            "MARKDOWN / CLEAR": "#f97316",
            "WATCH / VOLATILE": "#7c3aed",
            "HEALTHY": "#16a34a",
        },
    )

    decision_grid.update_traces(marker=dict(size=9, opacity=0.72))
    decision_grid.add_vline(
        x=0.5,
        line_dash="dash",
        line_color="#94a3b8",
        annotation_text="High Overstock Threshold",
        annotation_position="top left",
    )
    decision_grid.add_hline(
        y=0.5,
        line_dash="dash",
        line_color="#94a3b8",
        annotation_text="High Stockout Threshold",
        annotation_position="bottom right",
    )

    st.plotly_chart(chart_style(decision_grid), use_container_width=True)

    st.markdown(
        """
        <div class="insight-box">
            <b>Decision logic:</b><br>
            High stockout / low overstock → <b>REORDER NOW</b><br>
            Low stockout / high overstock → <b>MARKDOWN / CLEAR</b><br>
            High stockout / high overstock → <b>WATCH / VOLATILE</b><br>
            Low stockout / low overstock → <b>HEALTHY</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


else:
    hero(
        "Business Insights",
        "Actual observations generated from the supplied retail dataset.",
    )

    insight_text = (ROOT / "reports/eda_report.md").read_text(encoding="utf-8")
    st.markdown(insight_text)

    st.markdown('<div class="section-title">Supporting Charts</div>', unsafe_allow_html=True)

    chart_1, chart_2 = st.columns(2)

    with chart_1:
        st.image(
            ROOT / "reports/figures/weekly_demand.png",
            caption="Total Weekly Demand",
            use_container_width=True,
        )

    with chart_2:
        st.image(
            ROOT / "reports/figures/top_skus.png",
            caption="Top 10 SKUs by Units Sold",
            use_container_width=True,
        )

    st.image(
        ROOT / "reports/figures/category_demand.png",
        caption="Demand by Category",
        use_container_width=True,
    )