# Product Requirements Document (PRD)

## Project Overview

Time Warp is a human-curated, chronological archive for discovering live music footage on YouTube without algorithmic feeds. It enables people to share and explore concert videos based on when the performance occurred, rather than what an algorithm chooses to surface.

This project is a new iteration of an earlier personal exploration. It is being developed from the ground up to reflect current skills, tooling, and architectural judgment, rather than to extend or maintain the original codebase.

---

## Problem Definition

There is no easy way to find good concert footage isolated from the rest of YouTube.

Concert videos exist independently from one another on YouTube, with no straightforward way to connect them temporally. As a result, users who want to explore live music footage without being guided by recommendation algorithms must either already know what they are looking for or sift through unrelated content.

This problem is worth solving because even YouTube search has increasingly become beholden to algorithmic ranking rather than intentional human sharing.

---

## Target Users

### Personas

- **Avid music fan**  
  Wants to share favorite live videos without repeatedly sending links to friends who may not care.

- **Less-knowledgeable music fan (discovery-driven)**  
  Wants to discover new artists and performances through exploration rather than recommendation feeds.

- **Less-knowledgeable music fan (context-driven)**  
  Wants to experience the sound and vibe of a particular time period, for nostalgia, research, or curiosity.

---

## Core Goals

### User-Level Goals

- Users can contribute a video they care about so that others may find it.
- Users can follow any one video with chronologically consistent clips.
- Users can choose a day and see a performance from that day.
- Users can see performances from the same general time period.
- Users avoid sorting through unrelated or algorithmically promoted content.

### System-Level Goals

- Users must be able to submit new videos.
- Videos must be organized and surfaced chronologically.
- Posts must remain tied to a specific date and be visible to any user browsing that date.

---

## Non-Goals

- Automatic ingestion or web scraping of YouTube content.
- Any content other than live music performances.
- Support for platforms other than YouTube.
- Ranking, recommendation, or “best of” algorithms.

---

## Functional Scope Boundaries

- The product is primarily about viewing, with lightweight contribution.
- The system responds only to explicit user actions.
- Value is created through shared contribution.
- Historical browsing is the dominant mode; asynchronous exploration is prioritized over real-time interaction.

---

## MVP Definition

### End-to-End MVP Capacity

A user can submit a YouTube video link along with manually entered metadata and see it permanently placed in its correct chronological location within a calendar-style archive.

### MVP Completion Criteria

- A user can add a video without external assistance or explanation.
- A second user can see all videos added by previous users.
- Calendar data persists across sessions.
- The core workflow does not depend on developer intervention.
- The calendar makes sense to a user without explanation.

### Non-Blocking Omissions

- The calendar UI may be minimal or unstyled.
- Metadata entry may be fully manual.
- There is no need for artist, venue, genre, or song databases.
- Browsing by date alone is sufficient.

---

## Success Metrics

### Adoption Signals

- Videos are added by different people.
- Users return to add more videos after their first visit.
- Users browse the site without contributing.
- Users browse content added since their last visit.

### Contribution Quality

- Videos align with the live music domain.
- Valid YouTube links are tied to correct dates.
- Users encounter videos they had not previously seen.

### Discovery Effectiveness

- Users browse chronologically without search.
- Videos are grouped visually by month and year.
- Temporal browsing feels meaningful without ranking.

### Friction and Failure

- Users hesitate or abandon submission due to metadata uncertainty.
- Users are confused about what types of videos are allowed.
- Users scroll briefly and leave without interacting.
- Users expect ranking or filtering that does not exist.

### System Reliability

- Added data survives reloads and time.
- Users trust that contributions persist.
- The system functions without administrator oversight.