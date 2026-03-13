import streamlit as st
from src.dashboard.queries import (
    load_inventory,
    load_orders,
    load_summary,
)
from src.dashboard.charts import (
    chart_abc_value,
    chart_value_by_status,
    chart_treemap_top_items,
    chart_orders_aging,
)
from src.dashboard.chat import ask

st.set_page_config(
    page_title="Inventory Report",
    page_icon="📦",
    layout="wide",
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

# --- Sidebar: filtros ---
st.sidebar.header("Filtros")

storerooms = sorted(inv["store_room"].dropna().unique())
selected_rooms = st.sidebar.multiselect(
    "Storeroom", storerooms, default=storerooms
)

abc_options = ["A", "B", "C"]
selected_abc = st.sidebar.multiselect(
    "Clasificacion ABC", abc_options, default=abc_options
)

status_filter = st.sidebar.radio(
    "Status",
    ["Todos", "Dead Stock", "Overstock", "Normal"],
    index=0,
)

# --- Aplicar filtros ---
filtered = inv[
    inv["store_room"].isin(selected_rooms)
    & inv["abc"].isin(selected_abc)
]

if status_filter == "Dead Stock":
    filtered = filtered[filtered["dead_stock"] == 1]
elif status_filter == "Overstock":
    filtered = filtered[filtered["overstock"] == 1]
elif status_filter == "Normal":
    filtered = filtered[
        (filtered["dead_stock"] == 0)
        & (filtered["overstock"] == 0)
    ]

# --- Header ---
st.title("Inventory Report Dashboard")

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Items", f"{summary['total_items']:,.0f}")
k2.metric(
    "Total Value",
    f"${summary['total_value']:,.0f}",
)
k3.metric(
    "Dead Stock",
    f"${summary['dead_stock_value']:,.0f}",
    delta=f"{summary['dead_stock_items']:,.0f} items",
    delta_color="inverse",
)
k4.metric(
    "Redundant Orders",
    f"${summary['redundant_value']:,.0f}",
    delta=f"{summary['redundant_orders']:,.0f} orders",
    delta_color="inverse",
)

st.divider()

# --- Graficas fila 1 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Valor por Clasificacion ABC")
    st.plotly_chart(
        chart_abc_value(filtered), use_container_width=True
    )

with col2:
    st.subheader("Distribucion de Valor por Status")
    st.plotly_chart(
        chart_value_by_status(filtered),
        use_container_width=True,
    )

# --- Graficas fila 2 ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 20 Items por Valor")
    st.plotly_chart(
        chart_treemap_top_items(filtered),
        use_container_width=True,
    )

with col4:
    st.subheader("Ordenes por Antiguedad")
    st.plotly_chart(
        chart_orders_aging(orders),
        use_container_width=True,
    )

st.divider()

# --- Chat AI ---
st.subheader("Chat AI — Pregunta sobre tu inventario")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ej: Cuantos items dead stock hay?"):
    st.session_state.chat_history.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            response = ask(
                prompt, st.session_state.chat_history[:-1]
            )
        st.markdown(response)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": response}
    )
