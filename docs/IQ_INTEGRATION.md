# IQ Integration

CRISOL uses a phased integration plan for Foundry IQ, Fabric IQ Ontology, and Work IQ.

## Foundry IQ

Phase 1 does not call Foundry IQ. The local `backend/app/data/knowledge` folder contains synthetic demonstration documents that can later become a grounded knowledge base.

Phase 2 should add grounded retrieval with citations, source filtering, and document-level traceability.

## Fabric IQ Ontology

Phase 1 uses a local NetworkX graph as the ontology implementation. The `fabric_adapter.py` module is the boundary for later Fabric-backed ontology mapping.

Phase 2 can replace or enrich local JSON with Fabric ontology entities while preserving the same graph relationships.

## Work IQ

Phase 1 includes synthetic Work IQ-style signals in `work_signals.json`. These signals describe meeting load, focus time, preferred learning slots, and interruption risk.

Live Work IQ data is not implemented in Phase 1.

## Boundaries

CRISOL must not ingest real employee names, emails, private schedules, production logs, secrets, or customer data during the synthetic phases.
