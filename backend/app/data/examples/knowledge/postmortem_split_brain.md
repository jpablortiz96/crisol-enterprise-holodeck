# Postmortem PM-SPLIT-009

Synthetic demonstration document.

## Summary

At 02:14 in synthetic incident PM-SPLIT-009, order writes were accepted by two database nodes after a simulated network partition. `SVC-orders` retried writes, and `SVC-checkout` displayed inconsistent confirmation states.

## Lessons

- Failover must validate write ownership before traffic restoration.
- Checkout retries should back off when order state is uncertain.
- Incident command must freeze risky writes before broad restarts.
- Recovery evidence should be captured before cleanup tasks.

## Follow-Up Practice

Learners should practice `SCN-214-CHECKOUT-SPLIT-BRAIN` before taking the SRE readiness assessment.
