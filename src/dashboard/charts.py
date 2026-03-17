import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

COLORS = {
    "Dead Stock": "#e74c3c",
    "Overstock": "#f39c12",
    "Normal": "#27ae60",
    "Redundant": "#e74c3c",
    "Valid": "#27ae60",
}

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#fafafa",
    margin=dict(t=10, l=10, r=120, b=30),
)

COMPACT_HEIGHT = 280


def _fmt(value: float) -> str:
    """Formatea valor a formato compacto: $1.2M, $54K, $800."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def _pct(part: float, total: float) -> str:
    """Retorna porcentaje formateado."""
    if total == 0:
        return "0%"
    return f"{part / total * 100:.1f}%"


def _add_status(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columna 'status' basada en flags dead_stock y overstock."""
    df = df.copy()
    conditions = [df["dead_stock"] == 1, df["overstock"] == 1]
    df["status"] = np.select(conditions, ["Dead Stock", "Overstock"], default="Normal")
    return df


def chart_capital_at_risk(inv: pd.DataFrame, summary: dict) -> go.Figure:
    """Barras horizontales: capital atrapado por tipo de riesgo."""
    categories = ["Dead Stock", "Overstock", "Redundant Orders"]
    values = [
        summary["dead_stock_value"],
        summary.get("overstock_value", 0),
        summary["redundant_value"],
    ]
    total = summary["total_value"]
    colors = ["#e74c3c", "#f39c12", "#e67e22"]

    fig = go.Figure(go.Bar(
        y=categories,
        x=values,
        orientation="h",
        marker_color=colors,
        text=[f"<b>{_fmt(v)}  ({_pct(v, total)})</b>" for v in values],
        textposition="auto", insidetextanchor="end", constraintext="none",
        texttemplate="%{text}",
        textfont=dict(size=13, color="white", shadow="0 0 8px rgba(0,0,0,0.8)"),
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        height=COMPACT_HEIGHT,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(autorange="reversed"),
        bargap=0.4,
    )
    return fig


def chart_value_by_storeroom(inv: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Barras horizontales: storerooms con mayor valor de inventario."""
    by_room = (
        inv.groupby("store_room")["inventory_value"]
        .sum()
        .nlargest(top_n)
        .sort_values()
    )
    total = by_room.sum()

    fig = go.Figure(go.Bar(
        y=by_room.index,
        x=by_room.values,
        orientation="h",
        marker_color="#3498db",
        text=[f"<b>{_fmt(v)}  ({_pct(v, total)})</b>" for v in by_room.values],
        textposition="auto", insidetextanchor="end", constraintext="none",
        textfont=dict(size=13),
        texttemplate="%{text}",
    ))
    fig.update_traces(
        marker=dict(color="#3498db"),
        textfont=dict(
            color="white",
            shadow="0 0 8px rgba(0,0,0,0.8)",
        ),
    )
    fig.update_layout(
        **DARK_LAYOUT,
        height=COMPACT_HEIGHT,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False, showgrid=False),
        bargap=0.3,
    )
    return fig


def chart_top_items(inv: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Barras horizontales: items mas caros, coloreados por status."""
    inv = _add_status(inv)
    top = inv.nlargest(top_n, "inventory_value").sort_values("inventory_value")

    fig = go.Figure(go.Bar(
        y=top["item_description"],
        x=top["inventory_value"],
        orientation="h",
        marker_color=top["status"].map(COLORS),
        text=[f"<b>{_fmt(v)}</b>" for v in top["inventory_value"]],
        textposition="auto", insidetextanchor="end", constraintext="none",
        texttemplate="%{text}",
        textfont=dict(size=13, color="white", shadow="0 0 8px rgba(0,0,0,0.8)"),
        customdata=top["status"],
        hovertemplate="%{y}<br>%{customdata}<br>$%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        height=COMPACT_HEIGHT,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False, showgrid=False),
        bargap=0.3,
    )
    return fig


def chart_orders_aging(orders: pd.DataFrame) -> go.Figure:
    """Barras apiladas: ordenes por antiguedad, separadas por tipo."""
    orders = orders.copy()
    bins = [0, 90, 180, 365, float("inf")]
    labels = ["0-90d", "90-180d", "180-365d", ">365d"]
    orders["age_bucket"] = pd.cut(orders["age_days"], bins=bins, labels=labels)

    orders["order_type"] = orders["redundant_order"].map(
        {1: "Redundant", 0: "Valid"}
    )

    grouped = (
        orders.groupby(["age_bucket", "order_type"], observed=False)["open_value"]
        .sum()
        .reset_index()
    )
    grouped["label"] = grouped["open_value"].apply(lambda v: f"<b>{_fmt(v)}</b>")

    fig = px.bar(
        grouped,
        x="age_bucket",
        y="open_value",
        color="order_type",
        barmode="stack",
        color_discrete_map={"Redundant": "#e74c3c", "Valid": "#27ae60"},
        text="label",
    )
    fig.update_traces(
        textposition="inside", insidetextanchor="middle",
        textfont=dict(size=13, color="white", shadow="0 0 8px rgba(0,0,0,0.8)"),
    )
    fig.update_layout(
        **DARK_LAYOUT,
        height=COMPACT_HEIGHT,
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        legend=dict(orientation="h", y=1.15),
        yaxis=dict(showticklabels=False, showgrid=False),
        bargap=0.3,
    )
    return fig


def chart_status_by_storeroom(inv: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Barras apiladas: proporcion dead stock/overstock/normal por storeroom."""
    inv = _add_status(inv)

    top_rooms = (
        inv.groupby("store_room")["inventory_value"]
        .sum()
        .nlargest(top_n)
        .index
    )
    inv = inv[inv["store_room"].isin(top_rooms)]

    grouped = (
        inv.groupby(["store_room", "status"])["inventory_value"]
        .sum()
        .reset_index()
    )

    totals = grouped.groupby("store_room")["inventory_value"].transform("sum")
    grouped["pct"] = (grouped["inventory_value"] / totals * 100).round(1)
    grouped["label"] = grouped.apply(
        lambda r: f"<b>{_fmt(r['inventory_value'])} ({r['pct']:.0f}%)</b>", axis=1
    )

    room_order = (
        grouped.groupby("store_room")["inventory_value"]
        .sum()
        .sort_values(ascending=True)
        .index
        .tolist()
    )

    fig = px.bar(
        grouped,
        y="store_room",
        x="inventory_value",
        color="status",
        orientation="h",
        barmode="stack",
        color_discrete_map=COLORS,
        category_orders={"store_room": room_order},
        text="label",
    )
    fig.update_traces(
        textposition="inside", insidetextanchor="middle",
        textfont=dict(size=13, color="white", shadow="0 0 8px rgba(0,0,0,0.8)"),
    )
    fig.update_layout(
        **DARK_LAYOUT,
        height=COMPACT_HEIGHT,
        xaxis_title="",
        yaxis_title="",
        legend_title="",
        legend=dict(orientation="h", y=1.15),
        xaxis=dict(showticklabels=False, showgrid=False),
        bargap=0.3,
    )
    return fig
