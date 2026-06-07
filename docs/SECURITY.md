# Security And Data Handling

## Data Classification

Repository scenarios and examples use `sanitized-training` data. Identifiers, organizations, incidents, accounts, and business contexts are fictional.

## No PII Policy

Do not add real employee names, customer names, email addresses, phone numbers, account identifiers, payment data, or confidential incident details. Scenario imports are checked for common sensitive patterns before use.

## Secret Handling

- Keep `.env` ignored.
- Do not place credentials in source, scenario packs, browser code, logs, or telemetry.
- Use managed identity where supported.
- Use Azure Key Vault or platform secret configuration for deployed secrets.
- Rotate any credential that is accidentally exposed.

## Scenario Import Guardrails

Scenario packs must pass structural validation and sensitive-content validation. The validator checks for email-like strings, public domains and URLs, phone-like values, token-like strings, payment-card-like patterns, and prohibited sensitive phrases.

Automated checks reduce risk but do not replace review. A responsible owner should verify business context, fictional identifiers, role suitability, and knowledge references before a pack is distributed.

## Human Oversight

Competence scores, manager fragility signals, certification alignment, and replay comparisons are training guidance. Human reviewers remain responsible for employment, access, certification, and operational decisions.

## Output Limitations

CRISOL uses deterministic modeled consequences and cited training knowledge. Time travel is a deterministic replay projection, not an exact production rollback. Certification alignment is not official certification status.

## No Production Action Execution

CRISOL does not connect scenario decisions to production control planes. It does not restart services, change databases, revoke real sessions, approve finance workflows, or alter customer environments.
