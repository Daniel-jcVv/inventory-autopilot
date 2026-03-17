import os
from openai import OpenAI
from sqlalchemy import text
from src.etl.database import get_engine

SYSTEM_PROMPT_TEMPLATE = (
    "Eres un asistente de inventarios. Respondes preguntas "
    "usando SQL contra una base de datos con estas tablas:\n\n"
    "TABLA: inventory (16,249 filas)\n"
    "Columnas: item_number, item_description, store_room, "
    "balance_on_hand, current_price, inventory_value, "
    "average_daily_usage, avg12mon_usage, inventory_turns, "
    "dead_stock (1/0), overstock (1/0), abc (A/B/C), "
    "dos (days of supply), reorder_risk (1/0), "
    "status_code, commodity, item_lead_time, "
    "last_used, last_recieved\n\n"
    "Valores de store_room: {storerooms}\n\n"
    "TABLA: orders (3,813 filas)\n"
    "Columnas: item_number, item_description, po_number, "
    "issue_date, order_qty, open_qty, open_value, price, "
    "supplier_name, redundant_order (1/0), age_days, "
    "required_date, boh\n\n"
    "TABLA: summary (1 fila, KPIs pre-calculados)\n"
    "Columnas: total_items, total_value, dead_stock_items, "
    "dead_stock_value, overstock_items, overstock_value, "
    "reorder_risk_items, reorder_risk_value, total_orders, "
    "redundant_orders, redundant_value, orders_over_1yr\n\n"
    "Reglas:\n"
    "- Genera SOLO queries SELECT.\n"
    "- Responde en espanol.\n"
    "- Si no es sobre inventario, di que solo ayudas con eso.\n"
    "- Formatea numeros con comas y simbolo $.\n"
    "- Se conciso pero informativo.\n"
    "- Cuando el usuario mencione 'room X' o 'storeroom X', "
    "usa el valor exacto de store_room de la lista de arriba "
    "(por ejemplo, si el usuario dice 'room 2', busca el valor "
    "que contenga '2' en la lista)."
)


def build_system_prompt() -> str:
    """Construye el system prompt con valores dinamicos de la DB."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT store_room FROM inventory ORDER BY store_room")
        )
        rooms = [row[0] for row in result if row[0] is not None]
    return SYSTEM_PROMPT_TEMPLATE.format(storerooms=", ".join(rooms))


def get_client() -> OpenAI:
    """Crea cliente OpenAI apuntando a Groq."""
    return OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )


def extract_sql(response_text: str) -> str | None:
    """Extrae query SQL del response del LLM."""
    if "```sql" in response_text:
        return response_text.split("```sql")[1].split("```")[0].strip()
    if "```" in response_text:
        return response_text.split("```")[1].split("```")[0].strip()
    return None


def validate_sql(query: str) -> bool:
    """Verifica que el query sea solo SELECT."""
    normalized = query.strip().upper()
    if not normalized.startswith("SELECT"):
        return False
    forbidden = [
        "UPDATE", "DELETE", "INSERT",
        "DROP", "ALTER", "CREATE", "TRUNCATE",
    ]
    return not any(word in normalized for word in forbidden)


def run_query(query: str) -> str:
    """Ejecuta query SQL y retorna resultado como texto."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())
    if not rows:
        return "Sin resultados."
    header = " | ".join(columns)
    lines = [header, "-" * len(header)]
    for row in rows[:50]:
        lines.append(" | ".join(str(v) for v in row))
    if len(rows) > 50:
        lines.append(f"... ({len(rows)} filas totales, mostrando 50)")
    return "\n".join(lines)


def ask(question: str, history: list[dict] | None = None) -> str:
    """Procesa una pregunta del usuario sobre inventario.

    Args:
        question: Pregunta en lenguaje natural.
        history: Historial de mensajes previos (opcional).

    Returns:
        Respuesta en lenguaje natural.
    """
    client = get_client()
    messages = [{"role": "system", "content": build_system_prompt()}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
    )
    assistant_msg = response.choices[0].message.content

    sql = extract_sql(assistant_msg)
    if sql and validate_sql(sql):
        query_result = run_query(sql)
        messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({
            "role": "user",
            "content": (
                f"Resultado del query:\n{query_result}\n\n"
                "Responde la pregunta original con estos datos."
            ),
        })
        final = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            max_tokens=1024,
        )
        return final.choices[0].message.content

    return assistant_msg
