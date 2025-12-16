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