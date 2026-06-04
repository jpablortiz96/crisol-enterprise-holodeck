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

## Terminal Simulation Demo

1. Run the seeded SRE incident.

   ```powershell
   cd backend
   python -m app.run_scenario --role ROLE-SRE
   ```

2. Call out the five visible parts of each turn.

   - Situation.
   - Learner decision.
   - NPC reactions.
   - Consequence delta.
   - Citations.

3. Highlight the consequence cascade.

   The first turn intentionally restarts checkout during database uncertainty, increasing severity and revenue-at-risk.

   Show the timeline branch graph and revenue-at-risk deltas after the first bad decision.

4. Highlight the recovery arc.

   Later turns freeze writes, escalate incident command, correlate telemetry, and restore traffic gradually.

5. Close on assessment.

   The final section prints competence score, dimension scores, failure modes, and a coach debrief.
