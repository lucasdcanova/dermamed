# Medical-software disclaimer

**DermaMed is a research prototype. It is not a medical device.**

This document is the canonical disclaimer for the repository. It is referenced
by the README, the LICENSE, and (in production-style use) would be surfaced in
the API response and any UI.

## 1. Not a medical device

DermaMed is **not** intended, designed, validated, or distributed for any of
the following:

- Clinical diagnosis of skin conditions.
- Screening or triage of patients.
- Treatment recommendations.
- Decision-making about referral, biopsy, excision, or therapy.
- Use as a "clinical decision support" tool in any regulated jurisdiction.

It is a **technical scaffold** that demonstrates how a multimodal
vision-language model (Google MedGemma 4B) can be wired into a typed FastAPI
pipeline with audit logging and structured output.

## 2. No regulatory clearance

DermaMed has **no regulatory clearance, registration, or marketing
authorization** in any jurisdiction. Specifically:

- **United States (FDA):** not cleared, not approved. No 510(k), no De Novo,
  no PMA, no Q-Sub or pre-submission. AI-based dermatology classifiers are
  typically Software as a Medical Device (SaMD), commonly Class II. The
  prototype has no Predetermined Change Control Plan (PCCP) per the FDA
  AI/ML Final Guidance.
- **European Union (MDR 2017/745):** not CE marked. Under **Rule 11** of
  Annex VIII, diagnostic-decision software for a condition where delayed
  diagnosis can cause death or irreversible deterioration (melanoma) is
  **Class IIb minimum**, requiring a notified body. The EU AI Act
  (Reg. 2024/1689) would additionally classify a deployed version as
  **high-risk AI** under Annex III; no AI-Act conformity assessment has
  been performed.
- **Brazil (ANVISA):** not registered. Under **RDC 657/2022** (specific to
  SaMD) read together with **RDC 751/2022** (medical devices) and
  **RDC 665/2022** (BPF / GMP), software with diagnostic intent over a
  serious condition is typically Classe II SaMD. No Cadastro or Registro
  has been filed.
- **United Kingdom (MHRA):** no UKCA mark, no inclusion in the Software and
  AI as a Medical Device pathway.
- **Canada (Health Canada):** no Medical Device Licence (MDL).
- **Australia (TGA):** no ARTG inclusion.

See [`REGULATORY_POSITION.md`](REGULATORY_POSITION.md) for a fuller
per-jurisdiction sketch and the IMDRF SaMD risk-category mapping.

## 3. Model limitations

The underlying model, **Google MedGemma 4B** (`google/medgemma-4b-it`), is
released by Google as a research model with explicit non-clinical limitations.
From the model's own documentation: it is intended to accelerate development
of healthcare AI, not to provide clinical answers. It has not been validated
for direct clinical use. See the model card on Hugging Face for the full
statement.

## 4. No validation, no QMS, no human factors

This repository contains:

- **No** prospective clinical study.
- **No** IRB / ethics-committee approval. (In Brazil: no CEP/CONEP submission
  under Resolução CNS 466/2012 or 510/2016.)
- **No** comparison against labeled ground truth on a held-out dermatology
  dataset (e.g. HAM10000, ISIC, BCN20000, PH2).
- **No** sensitivity / specificity / AUC / NPV / PPV numbers for any task.
- **No** subgroup analysis across skin tones (Fitzpatrick I–VI), ages, or body
  sites — the well-documented dermatology-AI fairness gap is **not**
  addressed here.
- **No** prospective safety surveillance or post-market monitoring plan.
- **No** ISO 13485 quality management system.
- **No** ISO 14971 risk management file, FMEA, or hazard analysis.
- **No** IEC 62304 software lifecycle documentation (Class B/C software).
- **No** IEC 62366 usability engineering file; **no human factors testing**,
  formative or summative.
- **No** MDCG 2019-16 cybersecurity assessment.

Any number a user sees in the response payload (probability, confidence,
urgency) is a **direct passthrough from the language model** and is not a
calibrated clinical metric. The "AI analysis" label in the code is a
technical descriptor of the call graph, not a claim about clinical accuracy.

## 5. Data, privacy, security

This repository does **not** implement:

- HIPAA-compliant storage or transit (US).
- GDPR-compliant processing of special-category health data (EU).
- LGPD-compliant processing of sensitive personal data (Brazil).
- De-identification, pseudonymization, or right-to-erasure pipelines.
- Encryption-at-rest with managed keys (KMS / HSM).
- Audit-grade tamper-evident logging.

The "audit log" in the codebase is a JSON-lines file. It is a structural
placeholder, not a compliance control.

## 6. If you found this repo via a portfolio

Lucas Dickel Canova, MD (the author) is a surgeon and endoscopist who also
performs dermatologic surgery. This repo was built as a personal R&D exercise
to explore the developer experience of building on top of MedGemma. It is
**not** a product, **not** a company, **not** a service offered to patients,
clinicians, or institutions.

If you are evaluating the author's work, please read this disclaimer as part
of the work itself: knowing what a project is **not** is part of building
medical software responsibly.

## 7. Contact

For questions about this prototype:

- Portfolio: <https://www.lucascanova.com.br/portfolio>
- Repository: <https://github.com/lucasdcanova/DermaMed>

For clinical dermatology concerns: see a board-certified dermatologist.
