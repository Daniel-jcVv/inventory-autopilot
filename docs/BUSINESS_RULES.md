# Business Rules — Inventory Report Generator

## Objetivo

Pipeline automatizado: Excel crudo de inventario (ERP) → limpieza → analisis → base de datos → dashboard → alertas.
Proyecto portfolio para CV Data Analyst / Data Engineer.

---

## Input

Archivo: `data/A3 INVENTORY.xlsx` (datos reales de ZF TRW, anonimizados)

| Hoja | Filas (limpias) | Columnas |
|------|-----------------|----------|
| Inventory by Storeroom | 16,249 | 61 |
| OPEN ORDER | 3,813 | 18 |
| ACTUAL INVENTORY | ignorada (resumen) | — |

---

## Tier 1 — Analytics (clean.py)

### Completados

| Feature | Logica | Columna generada |
|---------|--------|------------------|
| Dead Stock | BOH > 0 y Average Daily Usage == 0 | `Dead Stock` (1/0) |
| Overstock | BOH > Avg12Mon Usage * 12 y uso > 0 | `Overstock` (1/0) |
| Redundant Order | BOH >= Open Qty | `Redundant Order` (1/0) |
| Age Days | dias desde Issue Date hasta la orden mas reciente | `Age Days` (int) |
| Open Value | Open Qty * Price | `Open Value` (float) |

### Pendientes

| Feature | Logica | Columna generada |
|---------|--------|------------------|
| ABC Classification | Pareto sobre Inventory Value acumulado: A = top 80%, B = siguiente 15%, C = resto 5% | `ABC` (A/B/C) |
| Days of Stock (DOS) | BOH / Average Daily Usage. Items con uso == 0 → DOS = infinito (flag) | `DOS` (float) |
| Reorder Risk | Average Daily Usage > 0 y BOH < (Average Daily Usage * 30) — menos de 30 dias de stock | `Reorder Risk` (1/0) |
| Aging por proveedor | groupby Supplier → mean/max de Age Days en Open Orders | Tabla agregada en Summary |

---

## Tier 2 — Infraestructura

| Componente | Descripcion | Archivo |
|------------|-------------|---------|
| SQLite + SQLAlchemy | Tablas: inventory, open_orders, summary. En produccion se cambia a SQL Server con 1 linea de config | `src/database.py` |
| FastAPI | Endpoint POST /run-pipeline → ejecuta ETL, retorna JSON con KPIs | `api.py` |
| Dashboard | Streamlit + Plotly: KPIs, filtros por Storeroom/ABC/Dead Stock, graficas | `app.py` |
| Chat AI | Groq (Llama 3.3 70B): consultas SQL en lenguaje natural sobre SQLite | integrado en `app.py` |

---

## Tier 3 — ML y Prediccion

| Feature | Logica | Datos |
|---------|--------|-------|
| Prediccion de demanda | Generar 12 meses de consumo sintetico por item. Modelo: Prophet o ARIMA simple. Predecir proximo mes | Data sintetica generada desde Avg12Mon Usage + ruido |
| Clustering k-means | Agrupar items por: Inventory Value, Average Daily Usage, DOS. Identificar patrones (alto valor/bajo uso, etc.) | Columnas existentes del inventario |

---

## Tier 4 — Automatizacion

### Escenario de produccion

```
1. Cada lunes el ERP exporta Excel de inventario
2. n8n detecta archivo nuevo en carpeta (File Trigger)
3. n8n llama a FastAPI POST /run-pipeline (HTTP Request)
4. Python limpia, analiza, guarda en SQLite
5. n8n envia reporte por email al gerente (Email node)
6. n8n manda alerta a Slack si dead stock > $5M (Slack node)
```

### Deploy

- Dashboard: Streamlit Cloud
- API: Railway o Render
- n8n: Docker (self-hosted)

---

## Stack

| Herramienta | Uso |
|-------------|-----|
| pandas | ETL, limpieza, analisis |
| openpyxl | Export Excel formateado |
| SQLAlchemy + SQLite | Base de datos (swap a SQL Server en produccion) |
| FastAPI | API REST |
| Streamlit + Plotly | Dashboard interactivo |
| Groq | Chat AI (consultas SQL) |
| scikit-learn | Clustering k-means |
| Prophet / statsmodels | Prediccion de demanda |
| n8n | Orquestacion automatica |
| Docker | Containerizacion |
| Git + GitHub | Control de versiones |

---

## Columnas clave del inventario

| Columna | Tipo | Uso |
|---------|------|-----|
| Balance On Hand (BOH) | int | Stock actual |
| Average Daily Usage | float | Consumo diario promedio |
| Avg12Mon Usage | float | Consumo promedio 12 meses |
| Inventory Value | float | Valor monetario del stock |
| Current Price | float | Precio unitario |
| Item Creation Date | date | Fecha de creacion |
| Last Used | date | Ultimo uso |
| Last Recieved | date | Ultima recepcion |
| Storeroom | str | Almacen |

## Columnas clave de ordenes

| Columna | Tipo | Uso |
|---------|------|-----|
| Open Qty | int | Cantidad pendiente |
| Price | float | Precio unitario |
| BOH | int | Balance On Hand (duplicado del inventario) |
| Issue Date | date | Fecha de emision |
| Required Date | date | Fecha requerida |
| Supplier | str | Proveedor |
