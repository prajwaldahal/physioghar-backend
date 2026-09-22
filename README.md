# PhysioGhar API

A FastAPI backend for the PhysioGhar therapist app. It mirrors the repository interfaces the
Flutter app defines, so the app can read from it instead of its bundled mock data without any
change above its repository layer.

State is held in memory and seeded from the same JSON the app ships with, so both sides start from
an identical dataset. There is no database and no authentication.

## Running

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API then listens on `http://127.0.0.1:8000`. Interactive docs are at `/docs`, and the OpenAPI
schema at `/openapi.json`.

Copy `.env.example` to `.env` to change the app name, the API prefix or the allowed CORS origins.
Every setting has a sensible default, so the file is optional.

Requires Python 3.11 or newer (developed on 3.12).

## Endpoints

All routes are under `/api/v1`. Bodies and responses use the same camelCase field names as the app.

### Profile and availability

| Method | Path | What it does |
|---|---|---|
| `GET` | `/profile` | The therapist profile. |
| `PUT` | `/profile` | Updates it. Validates a 10-digit phone, a well-formed email and experience between 0 and 60. |
| `GET` | `/availability` | The Available/Unavailable flag. |
| `PUT` | `/availability` | Sets it. |

### Schedule

| Method | Path | What it does |
|---|---|---|
| `GET` | `/slots?day=YYYY-MM-DD` | That day's slots, each resolved to `open`, `booked` or `blocked`. A booked slot carries its session. Omit `day` for the whole seeded horizon. |
| `POST` | `/slots` | Adds a 60-minute slot from `startsAt`. Rejects anything overlapping an existing slot. |
| `POST` | `/slots/{id}/block` | Blocks an open slot. A booked slot cannot be blocked. |
| `POST` | `/slots/{id}/unblock` | Reopens a blocked slot. |

### Bookings

| Method | Path | What it does |
|---|---|---|
| `GET` | `/bookings` | All sessions, or one status via `?status=pending\|upcoming\|completed\|cancelled\|declined`. |
| `GET` | `/bookings/{id}` | One session. |
| `POST` | `/bookings/{id}/accept` | Pending to upcoming, which books the slot. |
| `POST` | `/bookings/{id}/decline` | Pending to declined. |
| `POST` | `/bookings/{id}/complete` | Upcoming to completed, with optional `remarks`. |
| `POST` | `/bookings/{id}/reschedule` | Moves an upcoming session to a new `startsAt`. |

### Patients and notes

| Method | Path | What it does |
|---|---|---|
| `GET` | `/patients` | Every patient, each with their last session date and completed history. |
| `GET` | `/patients/{id}` | One patient with the same derived fields. |
| `GET` | `/notes?patientId=` | Notes, newest first, optionally for one patient. |
| `POST` | `/notes` | Adds a note. The note text is required; exercises and the next-session plan are optional. |
| `PUT` | `/notes/{id}` | Edits a note, keeping its original creation time and stamping `updatedAt`. |

### Complaints and state

| Method | Path | What it does |
|---|---|---|
| `GET` | `/complaints` | Complaints, newest first. |
| `POST` | `/complaints` | Submits one. Subject 5 to 80 characters, description 20 to 500, and a category from the fixed list. Returns a generated `PG-#####` reference. |
| `POST` | `/reset` | Puts every slice back to its seed. This is what the app's logout calls. |

`GET /health` sits outside the versioned prefix and answers `{"status": "ok"}`.

## Business rules

The rules live in `app/services/` rather than in the route handlers, and they match the app's
behaviour exactly:

- **A slot's booked state is derived, never stored.** A slot record only knows whether it is open or
  blocked; whether it is booked comes from matching its time against the sessions. A session and
  its slot therefore cannot disagree.
- **No double booking.** Accepting a request or rescheduling checks that a slot exists at that time,
  is not blocked, and is not already held by another session. Any failure returns `409` with a
  message that says what to do next.
- **Pending requests do not reserve a slot**, which is what makes a genuine clash possible. The seed
  contains two requests at the same time and one landing on a blocked slot, so both rejection paths
  can be exercised straight away.
- **Only upcoming sessions can be completed or moved**, and a request that has already been handled
  cannot be handled again.

## Project structure

```
app/
├── main.py                 FastAPI app, CORS, router mounting
├── core/config.py          settings, read from the environment
├── api/
│   ├── deps.py             the store dependency
│   └── v1/
│       ├── router.py       aggregates the endpoint routers
│       └── endpoints/      one module per resource
├── schemas/                enums, response models, request payloads
├── services/               business rules
├── repositories/           in-memory store and the seed JSON
└── utils/dates.py          slot arithmetic and relative-date resolution
```

## Assumptions

1. **No authentication.** The app has a single therapist, so every request acts as that therapist.
2. **State is in memory.** Restarting the server reseeds it. `POST /reset` does the same on demand.
3. **Dates in the seed are relative.** Sessions and notes are stored as a day offset from today plus
   a time, resolved at load, so the sample data always lands on the current week. Slots come from a
   per-weekday template for the same reason.
4. **Slots are a fixed 60 minutes**, and overlap is checked as a real interval overlap rather than
   an exact start-time match.
5. **Rule violations return `409`**, missing records `404`, and malformed payloads `422`.
6. **Complaint references are generated locally** in a `PG-#####` format; a real system would issue
   these from the admin side.
7. **CORS is open by default** so the app can call the API from an emulator. Narrow
   `CORS_ORIGINS` before putting this anywhere real.

## What I would do next with more time

- Persist to a real database instead of the in-memory store; the repository layer is already the
  seam for it.
- Add authentication and scope every route to the signed-in therapist.
- Move slot generation from a template to stored availability rules, so a therapist could set
  recurring weekly hours.
- Paginate the bookings and notes listings, which would start to matter with a real caseload.
