# Agents

CRISOL is organized around five functional agents. Phase 1 documents their responsibilities and prepares data for later implementation.

## Director

The Director chooses the simulation context. It selects a learner, target role, scenario seed, systems under stress, stakes, and time constraints.

## NPC Ensemble

The NPC Ensemble represents synthetic participants in the scenario. Examples include a support lead, database owner, compliance reviewer, customer success manager, and engineering manager.

## Consequence Engine

The Consequence Engine reads the ontology graph to identify affected systems, contract exposure, certification gaps, and likely business consequences.

## Examiner

The Examiner compares learner decisions with expected competencies. It scores incident triage, observability, recovery planning, communication, escalation judgment, and role-specific requirements.

## Coach

The Coach turns the Examiner output into a learning plan. It recommends practice scenarios, study hours, certification paths, and skill remediation.

## Phase 1 Scope

Phase 1 implements the graph and calculation foundation. Agent behavior is documented here for later implementation.
