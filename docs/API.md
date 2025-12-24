# API Specification (Human-Readable)

## Design Principles

- Clip is the canonical read model.
- Submission is the write path and audit trail.
- Chronological ordering is the only ordering.
- Validation and creation occur in a single request.

---

## Endpoints

### POST /contributors ✅ Implemented

Creates a contributor identity.

Request:
- display_name (optional)
- external_id (optional)

Response (201 Created):
- id (public_id, format: `ctr_<hex>`)
- display_name
- external_id
- created_at (RFC3339 format with trailing Z)

---

### POST /submissions ✅ Implemented

Creates a Submission, validates input, and creates a Clip on success.

Request:
- contributor_id (required)
- raw_youtube_input (required)
- raw_date_input (required, format: YYYY-MM-DD)
- title (optional)
- notes (optional)

Response (201 Created):
- id (public_id, format: `sub_<hex>`)
- contributor_id
- clip_id (public_id, format: `clp_<hex>`, null if rejected)
- status ("accepted" or "rejected")
- validation_error (string, null if accepted)
- raw_youtube_input
- raw_date_input
- title
- notes
- submitted_at (RFC3339 format with trailing Z)

Duplicate clip handling:
- If a clip with the same (youtube_video_id, performance_date) already exists, returns 409 Conflict
- Submission is still created with status="rejected" and validation_error indicating duplicate

---

### GET /submissions/{id} ✅ Implemented

Retrieves a submission record by its public_id.

Response (200 OK):
- Same format as POST /submissions response

Response (404 Not Found):
- detail: "Not found"

---

### GET /clips ⏳ Not yet implemented

Lists clips ordered by performance_date.

Query parameters:
- from (optional, date format: YYYY-MM-DD)
- to (optional, date format: YYYY-MM-DD)
- limit (optional, default: 50, max: 200)
- cursor (optional, for pagination)

---

### GET /clips/{id} ⏳ Not yet implemented

Retrieves a single clip by its public_id.

---

## Validation Rules

- raw_youtube_input must resolve to a YouTube video ID.
- raw_date_input must parse to YYYY-MM-DD.
- performance_date is required for Clip creation.
- (youtube_video_id, performance_date) pairs must be unique.

---

## Error Format

Errors are returned as structured JSON with a code, message, and optional details.