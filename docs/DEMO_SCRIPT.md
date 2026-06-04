# Demo Script

## 3-Minute Phase 1 Demo

1. Open with the problem.

   Enterprises know course completion, but they rarely know who is ready for a high-stakes operational moment.

2. Show the ontology load.

   Run:

   ```powershell
   cd backend
   python -m app.ontology.load
   ```

   Point out node counts, edge counts, affected systems for `SVC-checkout`, and revenue-at-risk.

3. Show the health endpoint.

   Run:

   ```powershell
   uvicorn app.main:app --reload
   ```

   Open `/health` and confirm the service is running.

4. Show revenue-at-risk.

   Open `/ontology/revenue-at-risk?systems=SVC-checkout` and explain how a checkout outage cascades through dependent systems and contracts.

5. Close with the next phase.

   Phase 2 adds grounded knowledge retrieval with citations and richer simulation behavior.
