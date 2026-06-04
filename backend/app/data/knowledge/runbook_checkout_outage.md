# Runbook KB-CHECKOUT-001

Synthetic demonstration document.

## Purpose

Use this runbook when `SVC-checkout` has elevated errors, latency, or failed order handoff to `SVC-orders`.

## First Actions

- Confirm whether checkout failures are isolated or tied to `SVC-orders`, `SVC-payments`, or `SVC-identity`.
- Check recent deployments and feature flags.
- Preserve request IDs and trace samples before restarting workers.
- If writes may be inconsistent, pause risky write paths before retry storms expand impact.

## Escalation

Escalate to the synthetic incident channel when checkout failure rate exceeds 10 percent for 10 minutes or when contract `CON-2031` is inside a critical revenue window.
