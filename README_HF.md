---
title: PsychoCrowd API
emoji: 🧠
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# PsychoCrowd API

Backend FastAPI for the PsychoCrowd psychometric simulation platform.

## Endpoints

- `GET /` — API status
- `POST /api/run-pipeline` — Run the full simulation pipeline
- `GET /api/report` — Get the latest report
- `POST /api/ai/interpret-rasch` — AI pedagogical interpretation
- `POST /api/ai/chat` — Analytical chat
- `POST /api/ai/generate-article` — Scientific article generation

## Environment Variables

Set the following secrets in your HF Space settings:

- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
