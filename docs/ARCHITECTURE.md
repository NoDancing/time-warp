# System Architecture

## Overview

Time Warp is a simple client-server system focused on durable storage and chronological retrieval of user-submitted data.

The system is intentionally minimal to support manual workflows and avoid algorithmic behavior.

---

## High-Level Components

- **Client (Web UI)**  
  Handles browsing and submission of clips.

- **API Service**  
  Validates submissions, persists data, and serves chronological queries.

- **Persistent Storage**  
  Stores Clips, Submissions, and Contributors.

---

## Architectural Constraints

- No background scraping or ingestion.
- No automated ranking or recommendation.
- All state transitions originate from explicit user actions.
- Chronological ordering is deterministic and stable.

---

## Data Flow (MVP)

1. User submits a YouTube link and date.
2. API validates input and records a Submission.
3. If valid, a Clip is created and persisted.
4. Browsing clients request Clips ordered by performance date.

---

## Implementation Status

### Completed ✅
- Contributor creation (POST /contributors)
- Submission creation with validation (POST /submissions)
  - Validates YouTube URL and date format
  - Creates Clip on successful validation
  - Handles duplicate clips (409 Conflict)
  - Always persists Submission record (even when rejected)
- Submission retrieval (GET /submissions/{id})
- Clip listing (GET /clips) with date filtering and pagination
- Clip retrieval (GET /clips/{id})
- Database persistence with public_id identifiers
- Unique constraint on (youtube_video_id, performance_date)

---

## Technology Stack

- **Backend**: Django 6.0 + Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Testing**: pytest + pytest-django
- **API Format**: JSON, RFC3339 timestamps