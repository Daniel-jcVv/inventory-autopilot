import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def chart_abc_value(inv: pd.DataFrame) -> go.Figure:
    """Barras horizontales: valor de inventario por categoria ABC."""
    abc = inv.groupby("abc")["inventory_value"].sum().reindex(["C", "B", "A"])
    fig = px.bar(
        x=abc.values,
        y=abc.index,
        orientation="h",
        color=abc.index,
        color_discrete_map={"A": "#e74c3c", "B": "#f39c12", "C": "#27ae60"},
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Valor ($)")
    return fig


def chart_value_by_status(inv: pd.DataFrame) -> go.Figure:
    """Donut chart: distribucion del valor de inventario por status."""
    conditions = [
        inv["dead_stock"] == 1,
        inv["overstock"] == 1,
    ]
    labels = ["Dead Stock", "Overstock", "Normal"]
    inv = inv.copy()
    inv["status"] = np.select(conditions, labels[:2], default="Normal")

    status_value = inv.groupby("status")["inventory_value"].sum()
    status_value = status_value.reindex(labels)

    colors = {"Dead Stock": "#e74c3c", "Overstock": "#f39c12", "Normal": "#27ae60"}

    fig = go.Figure(go.Pie(
        labels=status_value.index,
        values=status_value.values,
        hole=0.45,
        marker_colors=[colors[s] for s in status_value.index],
        textinfo="label+percent",
        hovertemplate="%{label}: $%{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(showlegend=False)
    return fig


def chart_treemap_top_items(inv: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Treemap: top items por valor de inventario, coloreados por status."""
    inv = inv.copy()
    conditions = [
        inv["dead_stock"] == 1,
        inv["overstock"] == 1,
    ]
    inv["status"] = np.select(conditions, ["Dead Stock", "Overstock"], default="Normal")

    top = inv.nlargest(top_n, "inventory_value")

    colors = {"Dead Stock": "#e74c3c", "Overstock": "#f39c12", "Normal": "#27ae60"}
    top["color"] = top["status"].map(colors)

    fig = go.Figure(go.Treemap(
        labels=top["item_description"],
        parents=[""] * len(top),
        values=top["inventory_value"],
        marker_colors=top["color"],
        textinfo="label+value",
        texttemplate="%{label}<br>$%{value:,.0f}",
        hovertemplate="%{label}<br>$%{value:,.0f}<br>%{customdata}<extra></extra>",
        customdata=top["status"],
    ))
    fig.update_layout(margin=dict(t=30, l=10, r=10, b=10))
    return fig


def chart_orders_aging(orders: pd.DataFrame) -> go.Figure:
    """Barras apiladas: ordenes por antiguedad, separadas por redundante/valida."""
    orders = orders.copy()
    bins = [0, 90, 180, 365, float("inf")]
    labels = ["0-90 dias", "90-180 dias", "180-365 dias", ">365 dias"]
    orders["age_bucket"] = pd.cut(orders["age_days"], bins=bins, labels=labels)

    orders["order_type"] = orders["redundant_order"].map(
        {1: "Redundante", 0: "Valida"}
    )

    grouped = (
        orders.groupby(["age_bucket", "order_type"], observed=False)["open_value"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        grouped,
        x="age_bucket",
        y="open_value",
        color="order_type",
        barmode="stack",
        color_discrete_map={"Redundante": "#e74c3c", "Valida": "#27ae60"},
    )
    fig.update_layout(
        xaxis_title="Antiguedad",
        yaxis_title="Valor ($)",
        legend_title="Tipo de Orden",
    )
    return fig
