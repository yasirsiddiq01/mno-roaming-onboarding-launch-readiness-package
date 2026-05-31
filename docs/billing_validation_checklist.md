# Roaming Billing Validation Checklist

This checklist defines billing and CDR validation checks for a simulated MNO roaming partner onboarding scenario.

The purpose is to confirm that roaming usage records, tariff checks, billing exceptions, reconciliation outputs, and settlement-related summaries are reviewed before launch readiness.

---

## 1. CDR Availability Checks

| Check | Acceptance Condition | Status |
|---|---|---|
| CDR generated | Usage record is generated after successful roaming session | Pending |
| Record ID present | Each CDR has a unique record identifier | Pending |
| IMSI present | Subscriber identifier is available | Pending |
| HPMN present | Home network identifier is available | Pending |
| VPMN present | Visited network identifier is available | Pending |
| Service type present | DATA, VOICE, SMS, or supported service type is identified | Pending |
| Timestamp present | Start and end time are available | Pending |

---

## 2. Mandatory Field Validation

| Field | Validation Rule | Status |
|---|---|---|
| record_id | Must not be empty and must be unique | Pending |
| imsi | Must match expected subscriber format | Pending |
| hpmn | Must match expected home network | Pending |
| vpmn | Must match onboarded roaming partner | Pending |
| service_type | Must be supported by tariff rules | Pending |
| tariff_id | Must exist in tariff table | Pending |
| charge_amount | Must be numeric and non-negative | Pending |
| currency | Must match agreed billing currency | Pending |

---

## 3. Rating and Tariff Validation

| Check | Acceptance Condition | Status |
|---|---|---|
| Tariff exists | Tariff ID is available for service type | Pending |
| DATA rating | Data charge matches MB × rate | Pending |
| VOICE rating | Voice charge matches duration × rate | Pending |
| SMS rating | SMS charge matches event-based rate | Pending |
| Rating mismatch | Any mismatch is flagged as billing exception | Pending |
| Currency mismatch | Any currency mismatch is flagged | Pending |

---

## 4. Billing Exception Review

| Exception Type | Review Action |
|---|---|
| Missing mandatory field | Correct source data or reject record |
| Duplicate CDR | Investigate duplicate generation or replay |
| Unknown tariff | Confirm tariff configuration |
| Rating mismatch | Compare actual and expected charge |
| Currency mismatch | Confirm billing agreement |
| Partner mismatch | Confirm VPMN/partner configuration |
| Timestamp issue | Check event generation and time synchronization |

---

## 5. Reconciliation Checks

| Check | Acceptance Condition | Status |
|---|---|---|
| Total records | Record count matches expected session volume | Pending |
| Total usage | Data/voice/SMS usage totals are reasonable | Pending |
| Total actual charge | Actual charges are summarized | Pending |
| Total expected charge | Expected charges are summarized | Pending |
| Difference amount | Billing difference is reviewed | Pending |
| Partner summary | Results are grouped by roaming partner | Pending |
| Service summary | Results are grouped by service type | Pending |

---

## 6. Launch Readiness Criteria

Billing validation is ready for launch when:

- mandatory CDR fields are present;
- duplicate records are reviewed;
- tariff configuration is confirmed;
- rating mismatches are resolved or accepted;
- reconciliation summary is reviewed;
- blocking billing exceptions are closed;
- billing validation report is attached to launch readiness review.

---

## 7. Notes

This checklist is part of a simulated portfolio project. It does not use real TAP files, real operator CDRs, private subscriber data, or confidential settlement records.