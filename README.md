# NTUA ECE SaaS 2025-2026 — saasPlug

## Ομάδα 26

Πλατφόρμα EV charging SaaS που επιτρέπει σε χρήστες να βρίσκουν και να κάνουν κρατήσεις φορτιστών από πολλαπλούς παρόχους.

---

## Αρχιτεκτονική Microservices

| Service | Port | Περιγραφή |
|---|---|---|
| orchestrator-service | 8080 | Κεντρικός συντονιστής, proxy για όλες τις κλήσεις |
| reservation-service | 8083 | Κρατήσεις + DB (MySQL) |
| search-service | 8087 | Αναζήτηση σημείων από εξωτερικούς παρόχους |
| registration-service | 8082 | Εγγραφή παρόχων |
| provider-statistics-service | 8081 | Στατιστικά ανά πάροχο |
| statistics-service | 8084 | Καθολικά στατιστικά (GlobalEvents) |
| invoice-service | 8085 | Τιμολόγια παρόχων |
| frontend | 3000 | React + Vite UI |

**Εξωτερικοί πάροχοι** (NTUA VPN απαιτείται):
- `redPlug` → `davinci.softlab.ntua.gr/saas26/redPlug/api`
- `greenPlug` → `davinci.softlab.ntua.gr/saas26/greenPlug/api`
- `bluePlug` → `davinci.softlab.ntua.gr/saas26/bluePlug/api`

---

## Εκκίνηση

Κάθε service έχει το δικό του `docker-compose.yml`. Εκκίνηση όλων:

```bash
docker compose -f orchestrator-service/docker-compose.yaml up -d
docker compose -f reservation-service/docker-compose.yml up -d
docker compose -f search_service/docker-compose.yaml up -d
docker compose -f registration-service/docker-compose.yaml up -d
docker compose -f provider-statistics-service/docker-compose.yaml up -d
docker compose -f statistics-service/docker-compose.yaml up -d
docker compose -f invoice-service/docker-compose.yaml up -d
docker network create shared-api-network
cd frontend && npm install && npm run dev
```

Το frontend είναι διαθέσιμο στο `http://localhost:3000`.

---

## Auth / Roles

| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Admin |
| `red plug` | `red plug` | Provider (redPlug) |
| `green plug` | `green plug` | Provider (greenPlug) |
| `blue plug` | `blue plug` | Provider (bluePlug) |
| οτιδήποτε άλλο | οτιδήποτε | User |

---

## Provider API Capabilities (από OpenAPI specs)

Και οι 3 providers υποστηρίζουν:
- **Live status**: per-point GET endpoint
- **Reservations**: POST endpoint

| Provider | Live Status | Reservation |
|---|---|---|
| redPlug | `GET /point/{id}` | `POST /reserve/{id}/{minutes}` |
| greenPlug | `GET /chargingPoints/{id}` | `POST /chargingPoints/{id}/reservations` |
| bluePlug | `GET /location/{id}/status` | `POST /location/{id}/hold?minutes=60` |

**Provider-specific statuses** (πέρα από available/reserved/malfunction):
- `redPlug`: `offline`, `charging`
- `greenPlug`: `held` (= reserved)
- `bluePlug`: standard

---

## Timezone

Όλα τα Docker containers τρέχουν σε **UTC**. Το frontend μετατρέπει σε local time (UTC+2) με:
```js
new Date(timestamp + 'Z').toLocaleString('el-GR', {...})
```
Και για expiry checks:
```js
new Date(endTime + 'Z') < new Date()
```
