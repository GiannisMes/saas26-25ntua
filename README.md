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

## Αλλαγές Frontend — Session 03/06/2026

### Νέα αρχεία

- `frontend/src/context/AuthContext.jsx` — Role-based auth με localStorage
- `frontend/src/pages/Login.jsx` — Login page με hints για credentials
- `frontend/src/components/PointPanel.jsx` — Reusable info panel για charging points
- `frontend/src/components/markerIcon.js` — Custom SVG colored markers ανά provider
- `frontend/src/context/useProviders.js` — Provider capabilities (hardcoded από OpenAPI specs)

### Τροποποιημένα αρχεία Frontend

**`frontend/src/App.jsx`**
- Role-based routing: admin → `/admin`, provider → `/provider/dashboard`, user → `/`
- `ProtectedRoute` με `roleHome()` για αποφυγή infinite redirect loops
- `NavLink` component με active tab highlighting (πράσινο underline)
- Navbar ανά role: user / provider / admin με διαφορετικά links
- Timezone-aware timestamps παντού (`endTime + 'Z'` για σωστό UTC parsing)

**`frontend/src/pages/MapSearch.jsx`** (User χάρτης)
- Split layout: χάρτης αριστερά + PointPanel δεξιά
- Colored SVG markers ανά provider (κόκκινο/πράσινο/μπλε)
- Click tracking → `POST /api/orchestrator/click`
- Reserve button με εκτιμώμενο κόστος (τιμή × ισχύς × 1h)

**`frontend/src/pages/ProviderDashboard.jsx`**
- Tab navigation μέσω `?tab=map|stats|invoices|reservations`
- Map tab: μόνο σημεία του συγκεκριμένου provider
- Stats tab: KPIs (Clicks, Κρατήσεις, Σύνολο events) + κατάσταση σημείων (live, δυναμικά statuses) + ημερήσια δραστηριότητα
- Invoices tab: σωστά field names (`invoice_id`, `billing_month`, `billing_year`, `total_points`, `price_per_point`)
- Reservations tab: κρατήσεις από DB φιλτραρισμένες ανά provider, active/cancelled toggle

**`frontend/src/pages/AdminDashboard.jsx`**
- Tab: **Χάρτης** — χάρτης με όλους τους providers, legend, PointPanel, reserve button
- Tab: **Στατιστικά** — KPI cards + bar charts ανά provider + ημερήσια δραστηριότητα + event breakdown
- Tab: **Υγεία** — όλα τα 7 services (orchestrator/reservation/search/registration/provider_stats/statistics/invoice) με UP/DOWN, parallel health checks, refresh button
- Tab: **Πάροχοι** — δυναμικά statuses (available/reserved/held/malfunction/offline/charging) που αθροίζουν σωστά στο σύνολο, κουμπί παραγωγής invoice ανά provider
- Tab: **Κρατήσεις** — διαχείριση κρατήσεων, active by default, cancelled/ληγμένες on demand toggle, αναλυτικές πληροφορίες σημείου (από join με search data)

**`frontend/src/pages/UserDashboard.jsx`**
- Πλήρης υλοποίηση "Κρατήσεις μου"
- Fetch από `/api/orchestrator/reservations/user/{userId}`
- Cross-reference με search data για address, τιμή, ισχύς, connector
- HTML entity decode για διευθύνσεις (`&amp;` → `&`)
- Κουμπί ακύρωσης κράτησης
- Active/cancelled toggle

**`frontend/src/components/PointPanel.jsx`**
- Εκτιμώμενο κόστος κράτησης πριν το reserve button

---

## Αλλαγές Backend — Session 03/06/2026

### orchestrator-service/main.py

**Νέα endpoints:**
- `POST /api/orchestrator/click` — Click tracking (global + provider stats, async)
- `GET /api/orchestrator/statistics/global` — Καθολικά στατιστικά (parallel calls)
- `GET /api/orchestrator/statistics/provider/{name}/detailed` — Αναλυτικά στατιστικά ανά provider
- `GET /api/orchestrator/admin/reservations` — Λίστα όλων των κρατήσεων (admin)
- `PUT /api/orchestrator/admin/reservations/{id}/cancel` — Ακύρωση χωρίς userId check
- `GET /api/orchestrator/reservations/user/{user_id}` — Κρατήσεις ανά χρήστη

**Performance βελτιώσεις:**
- `send_stat_event()` → non-blocking background thread (δεν καθυστερεί το response)
- `send_provider_stat()` → non-blocking background thread
- `/health` → parallel checks με ThreadPoolExecutor (από 6s → 2s)
- `/statistics/global` → 2 parallel requests
- `orchestrate_search` → fix double `.json()` bug

### reservation-service/main.py

**Νέα endpoints:**
- `GET /api/reservations/user/{user_id}` — Κρατήσεις ανά χρήστη
- `GET /api/admin/reservations` — Λίστα όλων + auto-expire
- `PUT /api/admin/reservations/{id}/cancel` — Admin cancel (bypass userId check)

**Bug fixes:**
- Auto-expire: `UPDATE ... SET status='CANCELLED' WHERE endTime < NOW()` πριν από κάθε fetch
- Fix null endTime: αν ο provider δεν επιστρέψει endTime, υπολογίζεται ως `now + duration`

### search_service/main.py

**Performance:**
- Parallel provider fetching με `ThreadPoolExecutor` — από sequential (3×5s=15s) σε parallel (max 5s)

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
