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
- id
- youtube_video_id
- youtube_url
- performance_date (YYYY-MM-DD)
- title
- notes
- created_at
- created_by_contributor_id
- added_via_submission_id

---

### Submission

A Submission records an attempt to add content and captures validation outcomes and friction signals.

Fields:
- id
- raw_youtube_input
- raw_date_input
- status
- validation_error
- submitted_at
- clip_id

---

### Contributor

A Contributor represents the person submitting clips, without enforcing an authentication model.

Fields:
- id
- display_name
- external_id
- created_at

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
- A Submission may exist without producing a Clip.
- Contributors do not own Clips beyond attribution.
- Chronological order is stable; new Clips are inserted, not reordered.