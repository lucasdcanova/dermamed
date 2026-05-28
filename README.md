# DermaMed

**Dermatology image-analysis research prototype.** A FastAPI backend that wires a
multimodal vision-language model (Google MedGemma 4B via the Hugging Face
Inference API) into a structured analysis schema (lesion characteristics,
ABCDE-style features, differential hypotheses).

> **Status:** R&D prototype, paused after MVP. Last active July 2025.
> Eight commits; backend pipeline functional against the demo endpoint; frontend
> stub only. Kept public as a reference implementation, not as a roadmap.

## Important disclaimer

**This is a research prototype. It is NOT a Software as a Medical Device
(SaMD). It is research code, not a device.**

- **Not for clinical, diagnostic, screening, or triage use.**
- **Not** FDA cleared, **not** CE marked, **not** ANVISA registered, **not**
  UKCA marked, **not** Health Canada licensed, **not** TGA listed.
- "AI analysis" in this repo means "a call to a language model returns a
  structured JSON". It has **no clinical validation, no IRB approval, and
  no human factors testing**. The probabilities in the response payload
  are not calibrated clinical metrics.
- Outputs of the underlying model (MedGemma 4B) are not validated for
  clinical decision-making. Google releases MedGemma as a research model
  with explicit non-clinical limitations.
- If this prototype were ever advanced to a product, the most likely
  classification path would be **FDA Class II SaMD / EU MDR Class IIb
  (Rule 11, since melanoma is potentially fatal) / ANVISA Classe II under
  RDC 657/2022**, plus EU AI Act high-risk obligations. It currently sits
  in none of those pathways.

See [`docs/DISCLAIMER.md`](docs/DISCLAIMER.md) for the full statement and
[`docs/REGULATORY_POSITION.md`](docs/REGULATORY_POSITION.md) for the
per-jurisdiction breakdown.

## What it actually does

```
image upload ──► preprocess (resize, normalize) ──► MedGemma 4B (HF Inference API)
                                                           │
                                                           ▼
                            structured JSON (Pydantic schemas):
                            - lesion characteristics (ABCDE-style)
                            - differential diagnosis (top-k with probabilities)
                            - risk stratification / urgency suggestion
                            - audit-log entry
```

- **Primary engine:** `backend/app/core/ai_engine_v2.py` — calls MedGemma via
  `huggingface_hub.InferenceClient`.
- **Fallback engine:** `backend/app/core/ai_engine_fallback.py` — deterministic
  stub so the demo endpoint works without GPU / model access.
- **API:** FastAPI with JWT auth, an authenticated `/analysis` route and an
  open `/analysis/demo` route used for portfolio demos.
- **Audit log:** every analysis writes a structured JSON line; the file is
  intentionally append-only to model what compliance scaffolding would look
  like (not production-grade).

## Stack

- **Backend:** Python 3.10+, FastAPI, Pydantic, `huggingface_hub`, PyTorch
  (optional, for local inference path)
- **Model:** `google/medgemma-4b-it` (multimodal, requires HF gated access)
- **Storage (planned):** PostgreSQL via Docker Compose
- **Cache (planned):** Redis
- **Frontend:** stub Next.js + Tailwind (not implemented beyond a single page)
- **Infra:** `docker-compose.yml` with backend + Postgres + Redis services

## Quick start

This repo is not packaged for end users. To explore it locally:

```bash
# 1. Get gated access to google/medgemma-4b-it on Hugging Face
#    https://huggingface.co/google/medgemma-4b-it
# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env: set HUGGINGFACE_TOKEN, SECRET_KEY, JWT_SECRET_KEY
# 3. Run
make install
make run-backend
# API docs: http://localhost:8000/docs
```

For an end-to-end run with database + cache:

```bash
make docker-up   # backend + postgres + redis
make docker-down
```

The demo endpoint (`POST /api/v1/analysis/demo`) returns a synthetic result
without requiring auth or model access.

## Repository layout

```
DermaMed/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes (auth, analysis, health)
│   │   ├── core/         # AI engines (v1, v2, fallback), config, logging
│   │   ├── schemas/      # Pydantic models for the analysis payload
│   │   └── main.py
│   ├── examples/         # sample inputs
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Next.js stub — not implemented beyond a page
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DISCLAIMER.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── MEDGEMMA_ACCESS.md
│   └── HUGGINGFACE_TOKEN_GUIDE.md
├── docker-compose.yml
├── Makefile
└── README.md
```

## What works, what doesn't

**Works:**
- Backend boots, OpenAPI docs render at `/docs`.
- `/analysis/demo` returns a structured, schema-valid mock response.
- MedGemma inference path is wired and runs against the HF Inference API given
  a valid gated-access token.
- JWT auth, request validation, audit logging.

**Doesn't:**
- No frontend beyond a static stub.
- No database persistence layer (schemas exist; no Alembic migrations, no real
  ORM-backed routes).
- No real-image clinical validation.
- No multi-image / longitudinal tracking.
- No EHR integration.

## Why this exists

Built by a surgeon who also does dermatologic surgery, as a hands-on
exploration of what the MedGemma 4B multimodal release would feel like inside
a realistic FastAPI / Postgres / Redis scaffold — schemas, audit log,
disclaimers, gated-access flow. Not a product, not a startup. A prototype to
learn the shape of the problem.

## Status & maintenance

- **Status:** paused (no active development since 2025-07-27).
- **Maintenance:** none. Issues and PRs may not be reviewed.
- **Next steps if resumed:** real frontend, persistence layer, clinical-image
  benchmark on a public dataset (HAM10000 / ISIC).

## Security

A research-grade `backend/.env` file containing development-time tokens was
committed to early history of this repository. Those credentials have been
(or are being) invalidated upstream. The current `HEAD` no longer tracks
`backend/.env`. Treat any string that *looks* like a token in the historical
tree as dead. For security disclosures, see [`SECURITY.md`](SECURITY.md).

## License

MIT — see [`LICENSE`](LICENSE).

## Author

**Lucas Dickel Canova, MD** — surgeon and endoscopist, Três Passos / RS,
Brazil. CRM 46.242 · RQE 39.549.

Portfolio: <https://www.lucascanova.com.br/portfolio>
