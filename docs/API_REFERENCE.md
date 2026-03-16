# API Reference

Base URL: `http://localhost:8001`

## Endpoints

### GET /health

Health check endpoint.

**Response:**

```json
{"status": "ok"}
```

### GET /summary

Returns aggregated inventory summary from the `summary` table.

**Response:**

```json
{
  "total_items": 16249,
  "total_value": 9150387,
  "dead_stock_items": 3795,
  "dead_stock_value": 5651897,
  "overstock_items": 1234,
  "overstock_value": 1915385
}
```

### GET /alerts

Returns inventory alerts with enterprise severity classification.

Severity is calculated based on dead stock percentage of total inventory value:

| Level | Dead Stock % | Severity |
|-------|-------------|----------|
| Healthy | < 5% | low |
| Warning | 5-15% | medium |
| Critical | 15-25% | high |
| Not competitive | > 25% | critical |

**Response:**

```json
{
  "severity": "critical",
  "dead_stock_pct": 61.8,
  "total_inventory_value": 9150387,
  "dead_stock": {
    "count": 3795,
    "total_value": 5651897
  },
  "overstock": {
    "count": 1234,
    "total_value": 1915385
  },
  "reorder_risk": {
    "count": 1871,
    "total_value": 390323
  },
  "abc": {
    "count": 1016,
    "total_value": 7318738
  }
}
```

## Integration with n8n

The `/alerts` endpoint is consumed by the n8n workflow `Inventory Alerts - Daily Report`:

```
Schedule Trigger (8:00 AM) --> GET /alerts --> If severity != "low" --> Gmail + Slack
```

The `severity` field drives the notification logic. Only `low` severity skips notifications.
