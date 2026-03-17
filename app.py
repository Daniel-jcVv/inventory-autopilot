import numpy as np
import streamlit as st
from src.dashboard.queries import (
    load_inventory,
    load_orders,
    load_summary,
    is_demo_mode,
)
from src.dashboard.charts import (
    chart_capital_at_risk,
    chart_value_by_storeroom,
    chart_top_items,
    chart_orders_aging,
    chart_status_by_storeroom,
)
from src.dashboard.insights import (
    insight_capital_at_risk,
    insight_value_by_storeroom,
    insight_top_items,
    insight_orders_aging,
    insight_status_by_storeroom,
)
from src.dashboard.chat import ask

st.set_page_config(
    page_title="Smart Inventory Management",
    page_icon="📦",
    layout="wide",
)

st.markdown("""
<style>
    /* KPI cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.18), rgba(142, 68, 173, 0.12));
        border: 1px solid rgba(52, 152, 219, 0.3);
        border-radius: 10px;
        padding: 15px 20px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        color: #fff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 700;
    }
    /* Graficos con fondo azul sutil */
    [data-testid="stPlotlyChart"] {
        background: rgba(52, 152, 219, 0.08);
        border: 1px solid rgba(52, 152, 219, 0.15);
        border-radius: 10px;
        padding: 10px;
        backdrop-filter: blur(4px);
    }
    /* Popover filtros */
    [data-testid="stPopover"] button {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    /* Sidebar chat */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* Insight cards */
    .insight-card {
        background: rgba(52, 152, 219, 0.08);
        border-left: 3px solid #3498db;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-top: 6px;
        margin-bottom: 24px;
        font-size: 0.85rem;
        line-height: 1.5;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(52, 152, 219, 0.15);
        border-left: 3px solid #3498db;
    }
    .insight-card .diagnosis {
        color: #ddd;
    }
    .insight-card .action {
        color: #f1c40f;
        margin-top: 6px;
        font-weight: 500;
    }
    /* Primary insight cards (fila superior) */
    .insight-card.primary {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.18), rgba(142, 68, 173, 0.12));
        border: 1px solid rgba(52, 152, 219, 0.3);
        border-left: 4px solid #3498db;
        padding: 14px 18px;
    }
    .insight-card.primary .diagnosis {
        color: #fff;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .insight-card.primary .action {
        color: #f1c40f;
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def show_insight(insight: dict, primary: bool = False):
    """Renderiza un insight card debajo de un grafico."""
    cls = "insight-card primary" if primary else "insight-card"
    st.markdown(
        f'<div class="{cls}">'
        f'<div class="diagnosis">{insight["diagnosis"]}</div>'
        f'<div class="action">Action: {insight["action"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def get_inventory():
    return load_inventory()


@st.cache_data(ttl=300)
def get_orders():
    return load_orders()


@st.cache_data(ttl=300)
def get_summary():
    return load_summary()


# --- Datos ---
inv = get_inventory()
orders = get_orders()
summary = get_summary()

# --- Sidebar: Chat AI ---
st.sidebar.header("Chat AI — Ask about your inventory")

if is_demo_mode():
    st.sidebar.info("Chat AI requires SQL Server. Running in demo mode (Excel data).")
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.sidebar.chat_message(msg["role"]):
            st.sidebar.markdown(msg["content"])

    if prompt := st.sidebar.chat_input("Ej: Cuantos items dead stock hay?"):
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )
        with st.sidebar.chat_message("user"):
            st.sidebar.markdown(prompt)

        with st.sidebar.chat_message("assistant"):
            with st.spinner("Consultando..."):
                response = ask(
                    prompt, st.session_state.chat_history[:-1]
                )
            st.sidebar.markdown(response)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

# --- Header + Filtros ---
st.title("Smart Inventory Management")

storerooms = sorted(inv["store_room"].dropna().unique())
status_options = ["Dead Stock", "Overstock", "Normal"]
risk_options = ["At Risk", "Safe"]


def toggle_all(prefix: str, items: list, key_all: str):
    """Sincroniza checkboxes individuales con Select All."""
    state = st.session_state[key_all]
    for item in items:
        st.session_state[f"{prefix}_{item}"] = state


_, fc1, fc2, fc3 = st.columns([4, 1, 1, 1])

with fc1:
    with st.popover("Storeroom", use_container_width=True):
        st.checkbox(
            "Select All", value=True, key="all_rooms",
            on_change=toggle_all,
            args=("room", storerooms, "all_rooms"),
        )
        selected_rooms = []
        for room in storerooms:
            if st.checkbox(room, value=True, key=f"room_{room}"):
                selected_rooms.append(room)

with fc2:
    with st.popover("Status", use_container_width=True):
        st.checkbox(
            "Select All", value=True, key="all_status",
            on_change=toggle_all,
            args=("status", status_options, "all_status"),
        )
        selected_status = []
        for s in status_options:
            if st.checkbox(s, value=True, key=f"status_{s}"):
                selected_status.append(s)

with fc3:
    with st.popover("Reorder Risk", use_container_width=True):
        st.checkbox(
            "Select All", value=True, key="all_risk",
            on_change=toggle_all,
            args=("risk", risk_options, "all_risk"),
        )
        selected_risk = []
        for r in risk_options:
            if st.checkbox(r, value=True, key=f"risk_{r}"):
                selected_risk.append(r)

# --- Aplicar filtros ---

filtered = inv[inv["store_room"].isin(selected_rooms)].copy()
conditions = [filtered["dead_stock"] == 1, filtered["overstock"] == 1]
filtered["status"] = np.select(
    conditions, ["Dead Stock", "Overstock"], default="Normal"
)
filtered = filtered[filtered["status"].isin(selected_status)]

risk_map = {"At Risk": 1, "Safe": 0}
risk_values = [risk_map[r] for r in selected_risk]
filtered = filtered[filtered["reorder_risk"].isin(risk_values)]

# --- Filtrar orders por storerooms seleccionados ---
items_in_rooms = inv[inv["store_room"].isin(selected_rooms)]["item_number"].unique()
filtered_orders = orders[orders["item_number"].isin(items_in_rooms)].copy()

# --- KPIs dinamicos (responden a filtros) ---
total_items = len(filtered)
total_value = filtered["inventory_value"].sum()
dead_stock_items = filtered[filtered["dead_stock"] == 1].shape[0]
dead_stock_value = filtered.loc[filtered["dead_stock"] == 1, "inventory_value"].sum()
redundant = filtered_orders[filtered_orders["redundant_order"] == 1]
redundant_count = len(redundant)
redundant_value = redundant["open_value"].sum()

st.markdown("")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Items", f"{total_items:,.0f}")
k2.metric("Total Value", f"${total_value:,.0f}")
k3.metric(
    "Dead Stock",
    f"${dead_stock_value:,.0f}",
    delta=f"{dead_stock_items:,.0f} items",
    delta_color="inverse",
)
k4.metric(
    "Redundant Orders",
    f"${redundant_value:,.0f}",
    delta=f"{redundant_count:,.0f} orders",
    delta_color="inverse",
)

st.markdown("")

# --- Graficas fila 1 ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='text-align:left'>Capital at Risk</h3>", unsafe_allow_html=True)
    filtered_summary = {
        "dead_stock_value": dead_stock_value,
        "overstock_value": filtered.loc[
            filtered["overstock"] == 1, "inventory_value"
        ].sum(),
        "redundant_value": redundant_value,
        "total_value": total_value,
    }
    st.plotly_chart(
        chart_capital_at_risk(filtered, filtered_summary),
        use_container_width=True,
    )
    show_insight(insight_capital_at_risk(filtered_summary), primary=True)

with col2:
    st.markdown("<h3 style='text-align:left'>Value by Storeroom</h3>", unsafe_allow_html=True)
    st.plotly_chart(
        chart_value_by_storeroom(filtered),
        use_container_width=True,
    )
    show_insight(insight_value_by_storeroom(filtered), primary=True)

# --- Graficas fila 2 ---
col3, col4 = st.columns(2)

with col3:
    st.markdown("<h3 style='text-align:left'>Top 10 Items by Value</h3>", unsafe_allow_html=True)
    st.plotly_chart(
        chart_top_items(filtered), use_container_width=True
    )
    show_insight(insight_top_items(filtered))

with col4:
    st.markdown("<h3 style='text-align:left'>Orders Aging</h3>", unsafe_allow_html=True)
    st.plotly_chart(
        chart_orders_aging(filtered_orders), use_container_width=True
    )
    show_insight(insight_orders_aging(filtered_orders))

# --- Grafica fila 3 ---
st.markdown("<h3 style='text-align:left'>Status Breakdown by Storeroom</h3>", unsafe_allow_html=True)
st.plotly_chart(
    chart_status_by_storeroom(filtered), use_container_width=True
)
show_insight(insight_status_by_storeroom(filtered))
