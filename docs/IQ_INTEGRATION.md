# IQ Integration

CRISOL uses a phased integration plan for Foundry IQ, Fabric IQ Ontology, and Work IQ.

## Foundry IQ

Phase 2 adds the first grounding interface. The local `backend/app/data/knowledge` folder is the approved synthetic knowledge base for development and tests.

The current implementation provides a deterministic local citation fallback. It loads markdown files, chunks them by heading or paragraph, searches by query term matches, and returns answers with citations.

Live Foundry IQ indexing and retrieval require Azure project and search configuration:

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT`
- `AZURE_SEARCH_ENDPOINT`
- `CRISOL_KNOWLEDGE_BASE`

Until those values and the live indexing flow are ready, the Foundry IQ adapter returns local cited results in `local-fallback` mode when configured, or `local` mode when not configured.

Every grounded answer must carry citations. If there are no citations, CRISOL returns a safe no-answer response.

## Fabric IQ Ontology

Phase 1 uses a local NetworkX graph as the ontology implementation. The `fabric_adapter.py` module is the boundary for later Fabric-backed ontology mapping.

Phase 2 can replace or enrich local JSON with Fabric ontology entities while preserving the same graph relationships.

## Work IQ

Phase 1 includes synthetic Work IQ-style signals in `work_signals.json`. These signals describe meeting load, focus time, preferred learning slots, and interruption risk.

Live Work IQ data is not implemented in Phase 1.

## Boundaries

CRISOL must not ingest real employee names, emails, private schedules, production logs, secrets, or customer data during the synthetic phases.

The build script validates the local synthetic documents only. It does not upload documents to Azure.
