# API Specification (Human-Readable)

## Design Principles

- Clip is the canonical read model.
- Submission is the write path and audit trail.
- Chronological ordering is the only ordering.
- Validation and creation occur in a single request.

---

## Endpoints

### POST /contributors

Creates a contributor identity.

Request:
- display_name
- external_id (optional)

Response:
- Contributor object

---

### POST /submissions

Creates a Submission, validates input, and creates a Clip on success.

Request:
- contributor_id
- raw_youtube_input
- raw_date_input
- title (optional)
- notes (optional)

Responses:
- Accepted submission with clip_id
- Rejected submission with validation_error
- Conflict if duplicate clip exists

---

### GET /submissions/{id}

Retrieves a submission record.

---

### GET /clips

Lists clips ordered by performance_date.

Query parameters:
- from (optional)
- to (optional)
- limit
- cursor

---

### GET /clips/{id}

Retrieves a single clip.

---

## Validation Rules

- raw_youtube_input must resolve to a YouTube video ID.
- raw_date_input must parse to YYYY-MM-DD.
- performance_date is required for Clip creation.
- (youtube_video_id, performance_date) pairs must be unique.

---

## Error Format

Errors are returned as structured JSON with a code, message, and optional details.