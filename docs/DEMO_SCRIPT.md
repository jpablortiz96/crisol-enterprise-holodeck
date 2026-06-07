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

6. Show the product report.

   Open `/reports/latest` and call out the cited evidence trail, skill gaps, certification alignment, and next best actions.

7. Show the manager view.

   Open `/manager/fragility-map`.

   After the run, show the cited competence report and manager fragility map.

## Browser War-Room Demo

1. Confirm Azure Speech before recording.

   Open:

   ```text
   http://127.0.0.1:8000/voice/status
   ```

   Confirm `configured` is `true` and `provider` is `azure-speech`.

2. Open War-Room.

   ```text
   http://localhost:3000
   ```

3. Play the live scenario.

   Click `Play Live Simulation`.

4. First 30 seconds.

   Show the animated NPC stage and synchronized Event Rail. The active speaker should remain highlighted while the matching voice line plays.

   Pause briefly on the first bad restart decision. Point out `Cascade detected`, `Revenue delta`, and synchronized `NPC pressure`, then resume playback.

   Use this line:

   "The NPC pressure is not just text. It is synthesized through Azure Speech so the simulation feels like a real incident room."

5. Show branching timeline.

   Use the center graph to explain the distinct root node, alarming cascade node, stabilizing recovery nodes, and animated active branch.

6. Final 30 seconds.

   Show `Competence Score`, the coach plan in the competence report, `Manager Fragility Map`, and the animated NPC roster.

7. Show playback control.

   Use `Replay Session` to restart the same buffered event sequence without rerunning the backend. Mention the `0.75x`, `1x`, and `1.25x` controls for recording pace.

8. Optional fallback callout.

   If speech is not configured, point to `Text fallback active` in the live event rail. The demo should continue without Azure credentials.

9. One-shot fallback path.

   Click `Run SRE Simulation` when you want the full deterministic session to appear at once instead of streamed playback.

## Phase 8 Platform Demo

1. Run the tool registry.

   ```powershell
   cd backend
   python -m app.mcp_server.server --list-tools
   python -m app.mcp_server.server --demo
   ```

2. Use this line:

   "CRISOL is also exposed as an MCP tool server, so another agent can run simulacrums programmatically."

3. Run or complete the SRE simulation in the War-Room.

4. Open `Time-Travel Replay` and select the first restart decision.

5. Use this line:

   "Then I branch from the bad restart and ask CRISOL: what if the learner had frozen writes instead?"

6. Choose `Freeze writes and identify primary database writer`, then click `Branch From This Decision`.

7. Compare competence score, peak revenue-at-risk, final severity, and cited reasoning. State that this is a deterministic replay projection, not an exact production rollback.

8. Open the `CRISOL MCP Server` panel and click `Run MCP Demo`.

9. Open `/grounding/learn/test?q=AZ-400%20monitoring%20CI/CD` and point out whether the response mode is `learn-mcp` or `local-fallback`.
