# Data Model & Domain Entities

## Domain Glossary

- **Clip**: A stored YouTube video representing a live performance.
- **Performance Date**: The date the performance occurred, used for chronological ordering.
- **Submission**: A user attempt to add a clip to the archive.
- **Contributor**: The actor submitting clips, anonymous or identified.

---

## Core Entities

### Clip

A Clip is the canonical, persistent record that powers browsing. It stores the stable identity of a YouTube video, the performance date used for chronological placement, and minimal display metadata.

Fields:
- public_id (primary identifier returned by API, format: `clp_<hex>`)
- contributor (ForeignKey to Contributor)
- youtube_video_id (extracted from raw_youtube_input)
- raw_youtube_input (original user input)
- performance_date (DateField, YYYY-MM-DD format)
- title (optional)
- notes (optional)
- created_at (DateTimeField)

Database Constraints:
- Unique constraint on (youtube_video_id, performance_date) to prevent duplicates

---

### Submission

A Submission records an attempt to add content and captures validation outcomes and friction signals. A Submission is always created, even if validation fails.

Fields:
- public_id (primary identifier returned by API, format: `sub_<hex>`)
- status ("accepted" or "rejected")
- contributor (ForeignKey to Contributor)
- clip (ForeignKey to Clip, null if rejected)
- validation_error (TextField, null if accepted)
- raw_youtube_input (original user input)
- raw_date_input (original user input, format: YYYY-MM-DD)
- title (optional, copied from submission to clip if accepted)
- notes (optional, copied from submission to clip if accepted)
- submitted_at (DateTimeField)

Status Values:
- "accepted": Submission passed validation and a Clip was created
- "rejected": Submission failed validation (invalid input or duplicate clip)

---

### Contributor

A Contributor represents the person submitting clips, without enforcing an authentication model.

Fields:
- public_id (primary identifier returned by API, format: `ctr_<hex>`)
- display_name (optional)
- external_id (optional, for external system integration)
- created_at (DateTimeField)

---

## Entity Relationships

- A Contributor may create zero or more Submissions.
- A Submission may result in zero or one Clip.
- A Clip is created from an accepted Submission.
- A Clip is attributed to exactly one Contributor.
- Clips are ordered exclusively by performance_date.

---

## Invariants

- A Clip cannot exist without a performance date.
- A Submission may exist without producing a Clip (status="rejected").
- Contributors do not own Clips beyond attribution.
- Chronological order is stable; new Clips are inserted, not reordered.
- (youtube_video_id, performance_date) pairs must be unique across all Clips.
- All entities use public_id for external identification (never expose Django's internal pk).
- Submissions are always persisted, even when validation fails (for audit trail).