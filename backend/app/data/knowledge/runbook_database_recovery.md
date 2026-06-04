# Runbook KB-DBREC-002

Synthetic demonstration document.

## Purpose

Use this runbook when `SVC-db` shows replication lag, write conflicts, failover uncertainty, or recovery point risk.

## Recovery Checks

- Identify the current writer and confirm that only one primary accepts writes.
- Check replication health before triggering failover.
- Capture recovery point and recovery time estimates.
- Coordinate with `SVC-orders`, `SVC-ledger`, and `SVC-data-pipeline` owners before reopening writes.

## Completion Criteria

Database recovery is complete when write ownership is stable, dependent services pass synthetic probes, and the incident lead approves traffic restoration.
