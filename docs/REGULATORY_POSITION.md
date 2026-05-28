# Regulatory position

> Companion to [`DISCLAIMER.md`](DISCLAIMER.md). The disclaimer answers
> "what is this not?". This document answers "where in the regulatory
> landscape would it sit *if* it were ever advanced toward a product?".

## TL;DR

DermaMed, **as it exists in this repository**, is research code. It is not a
Software as a Medical Device (SaMD). It is not in any regulatory pathway. No
notified body, no FDA pre-submission, no ANVISA Cadastro, no MHRA
registration, no Health Canada licence, no TGA inclusion. The repository is
public for portfolio reasons only.

If the prototype were ever taken toward a real product, the analysis below
sketches the most likely classification path. **None of this analysis has
been validated by a regulatory consultant**; it is the author's working
understanding and is provided so a reader can see where the work would
*start* if it were ever resumed.

## IMDRF SaMD risk framework

The International Medical Device Regulators Forum (IMDRF) SaMD framework
(N12: "Software as a Medical Device: Possible Framework for Risk
Categorization and Corresponding Considerations") classifies SaMD on two
axes:

1. **Significance of information provided to the healthcare decision**
   - Treat or diagnose
   - Drive clinical management
   - Inform clinical management

2. **Healthcare situation or condition**
   - Critical
   - Serious
   - Non-serious

A dermatology AI that produces a differential diagnosis with a melanoma
probability would, if marketed as a clinical tool, sit at approximately:

- **Significance:** "diagnose" (it returns a named differential).
- **Condition:** "serious" to "critical" (melanoma is potentially fatal;
  delayed diagnosis carries irreversible harm).

That intersection is **SaMD Category III or IV** in the IMDRF matrix — the
highest-risk SaMD tiers, generally treated as Class II in the US, Class IIa
or higher in the EU, and Class II under ANVISA.

DermaMed is therefore **not** a low-risk wellness app. If it were ever
deployed for clinical decisioning, it would land in the same regulatory
neighbourhood as commercial dermatology AI products such as DermAssist or
SkinVision (those are CE-marked Class IIa under EU MDR; SkinVision is also
TGA-listed; neither has, to the author's knowledge, US FDA clearance for the
same indication as of the last update of this file).

## Per-jurisdiction sketch (as of this writing)

### United States — FDA

- **Authority:** 21 CFR Part 820 (QSR, transitioning to QMSR via 21 CFR
  820.10), Section 513 (device classification), 21 CFR 807 (510(k)).
- **Expected pathway:** De Novo for a novel intended use, or 510(k) with a
  predicate (e.g. predicate classifiers for skin-lesion analysis exist).
- **Expected class:** Class II SaMD.
- **Additional:** Predetermined Change Control Plan (PCCP) under the
  FDA Final Guidance on AI/ML-enabled devices (2023+); cybersecurity
  documentation per FDA premarket guidance (2023); biocompatibility N/A
  (software-only).
- **Status of DermaMed:** none. No pre-sub, no Q-Sub, no QSR, no QMS.

### European Union — MDR 2017/745

- **Authority:** Regulation (EU) 2017/745 (MDR), in force since 2021.
- **Classification rule:** **Rule 11** (software intended to provide
  information used to make decisions for diagnostic or therapeutic
  purposes). Diagnostic-decision-influencing software for skin cancer
  triggers **Class IIa minimum, IIb if death or irreversible deterioration
  is possible** — for melanoma decisioning, IIb is a defensible position.
- **Notified body:** required (Class IIa and above).
- **Additional:** Technical documentation per Annexes II and III, post-
  market surveillance plan per Article 83, vigilance reporting per
  Article 87, **EU AI Act (Reg. 2024/1689) Annex III high-risk classification
  if used in healthcare and not exempt** — AI Act obligations stack on top
  of MDR.
- **Status of DermaMed:** none. No CE mark, no notified body engaged.

### Brazil — ANVISA

- **Authority:** RDC 751/2022 (medical devices) and **RDC 657/2022**
  (specific to software as a medical device — SaMD).
- **Expected class:** **Classe II** under RDC 657/2022, given diagnostic
  intent and a serious condition.
- **Expected pathway:** Cadastro or Registro depending on final class
  determination; technical dossier with clinical evaluation; Boas Práticas
  de Fabricação (BPF) via RDC 665/2022 for the manufacturer.
- **Additional:** LGPD (Lei 13.709/2018) for any processing of dado
  pessoal sensível (health data); ANPD orientations on AI processing.
- **Status of DermaMed:** none. No Cadastro, no Registro, no BPF.

### United Kingdom — MHRA

- **Authority:** UK MDR 2002 (as amended post-Brexit), with the MHRA's
  Software and AI as a Medical Device Change Programme in transition. UKCA
  mark required (CE accepted in Great Britain during the recognition
  window).
- **Status of DermaMed:** none.

### Canada — Health Canada

- **Authority:** Medical Devices Regulations (SOR/98-282), Class II–IV based
  on risk; SaMD guidance aligned with IMDRF.
- **Status of DermaMed:** no MDL (Medical Device Licence).

### Australia — TGA

- **Authority:** Therapeutic Goods Act 1989; software as a medical device
  reforms 2021. Class IIa expected for diagnostic-decision software; ARTG
  inclusion required.
- **Status of DermaMed:** no ARTG inclusion.

## Quality and clinical-evidence prerequisites (none of which are met)

If the prototype were advanced, the minimum scaffold before any clinical
deployment would include:

- **ISO 13485:2016** — medical device QMS.
- **ISO 14971:2019** — risk management; FMEA / hazard analysis for the
  full intended-use envelope.
- **IEC 62304:2006/Amd 1:2015** — software lifecycle processes; this
  prototype's code does not meet Class B requirements, let alone Class C.
- **IEC 62366-1:2015** — usability engineering; **no human factors / no
  formative or summative usability testing has been performed**.
- **ISO 14155:2020** — clinical investigation of medical devices for
  human subjects (when conducting clinical evaluation).
- **MDCG 2019-16** — cybersecurity guidance for medical devices.
- **Clinical evaluation** — prospective study, IRB / Comitê de Ética em
  Pesquisa (CEP/CONEP in Brazil) approval, defined endpoints, subgroup
  analysis across Fitzpatrick I–VI, age bands, anatomic sites.

**None of the above exists for this repository.** The repository contains
zero of these artifacts. That is fine for a research prototype and
disqualifying for a device.

## What this repository is, in regulatory terms

- A **research tool** as understood by FDA's framing of non-device research
  software (used internally to explore a hypothesis; not distributed for
  patient care).
- Not "exempt SaMD" — there is no such concept here; it is simply not SaMD.
- Not a "wellness device" under the FDA General Wellness guidance — it
  makes no wellness claims either.

If you are a regulatory reviewer landing on this repository: please read it
as a developer exercise. The author is a practising surgeon
(CRM 46.242, RQE 39.549) who is aware of the regulatory gap between this
code and a marketable device, and has documented that gap deliberately.

## See also

- [`DISCLAIMER.md`](DISCLAIMER.md) — canonical non-device statement.
- [`../SECURITY.md`](../SECURITY.md) — responsible disclosure policy.
- [`../README.md`](../README.md) — project overview and status.
