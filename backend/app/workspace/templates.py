from copy import deepcopy
from typing import Any


EDUKY_SKILLS = [
    {
        "skill_id": "SK-prioritization-under-pressure",
        "name": "Prioritization under pressure",
        "description": "Sequence actions by customer impact, reversibility, and business exposure.",
    },
    {
        "skill_id": "SK-customer-communication",
        "name": "Customer communication",
        "description": "Communicate impact, uncertainty, ownership, and next checkpoints clearly.",
    },
    {
        "skill_id": "SK-escalation-judgment",
        "name": "Escalation judgment",
        "description": "Escalate material risk to the correct decision owner at the correct time.",
    },
    {
        "skill_id": "SK-revenue-risk-control",
        "name": "Revenue-risk control",
        "description": "Protect revenue and trust while avoiding unsupported recovery actions.",
    },
    {
        "skill_id": "SK-launch-decision-making",
        "name": "Launch decision-making",
        "description": "Control launch scope, recovery sequencing, and stakeholder checkpoints.",
    },
    {
        "skill_id": "SK-operational-diagnosis",
        "name": "Operational diagnosis",
        "description": "Use available evidence to isolate failure paths and choose stabilizing actions.",
    },
    {
        "skill_id": "SK-automation-thinking",
        "name": "Automation thinking",
        "description": "Identify repeatable controls and safe automation opportunities.",
    },
    {
        "skill_id": "SK-brand-protection",
        "name": "Brand protection",
        "description": "Respond to public pressure while preserving credibility and customer trust.",
    },
    {
        "skill_id": "SK-student-success",
        "name": "Student success",
        "description": "Resolve learner-impacting issues through clear ownership and fair policy application.",
    },
    {
        "skill_id": "SK-data-informed-decision",
        "name": "Data-informed decision-making",
        "description": "Use operational evidence and business signals to make bounded decisions.",
    },
]

EDUKY_ROLES = [
    {
        "role_id": "ROLE-FOUNDER-OPERATOR",
        "title": "Founder Operator",
        "description": "Owns cross-functional decisions across support, launches, content, automation, and revenue risk.",
        "required_skills": [
            "SK-prioritization-under-pressure",
            "SK-escalation-judgment",
            "SK-revenue-risk-control",
            "SK-data-informed-decision",
        ],
    },
    {
        "role_id": "ROLE-STUDENT-SUCCESS",
        "title": "Student Success Lead",
        "description": "Owns learner support quality, policy execution, and escalation handling.",
        "required_skills": [
            "SK-customer-communication",
            "SK-student-success",
            "SK-escalation-judgment",
        ],
    },
    {
        "role_id": "ROLE-LAUNCH-MANAGER",
        "title": "Launch Manager",
        "description": "Coordinates launch readiness, access, checkout, content, and recovery decisions.",
        "required_skills": [
            "SK-launch-decision-making",
            "SK-operational-diagnosis",
            "SK-revenue-risk-control",
        ],
    },
    {
        "role_id": "ROLE-CONTENT-STRATEGIST",
        "title": "Content Strategist",
        "description": "Protects brand trust while coordinating content corrections and public response.",
        "required_skills": [
            "SK-brand-protection",
            "SK-customer-communication",
            "SK-data-informed-decision",
        ],
    },
    {
        "role_id": "ROLE-AUTOMATION-SPECIALIST",
        "title": "Automation Specialist",
        "description": "Designs safe operational workflows and repeatable decision support.",
        "required_skills": [
            "SK-automation-thinking",
            "SK-operational-diagnosis",
            "SK-prioritization-under-pressure",
        ],
    },
]

EDUKY_PROFILE = {
    "profile_id": "PROFILE-FOUNDER-001",
    "display_name": "Founder Operator",
    "role_id": "ROLE-FOUNDER-OPERATOR",
    "context": (
        "Runs a digital education business and makes decisions across support, "
        "launches, content, automation, and revenue risk."
    ),
    "data_classification": "sanitized-training",
}

EDUKY_KNOWLEDGE = {
    "eduky_support_policy.md": """# Eduky Support Policy

This sanitized training policy defines fair, consistent support handling for a fictional digital education workspace.

## Operating Rules

- Acknowledge learner impact before discussing internal ownership.
- Separate urgent access failures from standard guidance requests.
- Escalate repeated access, payment-state, or public-pressure signals.
- Record the decision owner and next checkpoint without storing personal contact data.
""",
    "eduky_refund_handling_guide.md": """# Eduky Refund Handling Guide

Use a consistent fictional policy during training scenarios.

## Decision Sequence

1. Confirm the affected product and policy window using sanitized identifiers.
2. Separate access remediation from refund eligibility.
3. Escalate public-pressure cases to the Founder Operator.
4. Communicate the decision, rationale, and next checkpoint without unsupported promises.
""",
    "eduky_launch_playbook.md": """# Eduky Launch Playbook

The launch team protects learner access, checkout integrity, and brand trust through staged controls.

## Launch Controls

- Validate checkout, entitlement, and access signals independently.
- Freeze promotional expansion when access integrity is uncertain.
- Use one launch command owner and a fixed checkpoint cadence.
- Restore traffic in stages after successful access verification.
""",
    "eduky_student_success_playbook.md": """# Eduky Student Success Playbook

Student-success decisions prioritize access restoration, policy clarity, and credible communication.

## Response Pattern

- State the confirmed learner impact.
- Name the current owner and next checkpoint.
- Avoid publishing private learner details.
- Close only after the affected learning path is verified.
""",
    "eduky_content_risk_playbook.md": """# Eduky Content Risk Playbook

This fictional playbook supports a measured response to public content pressure.

## Response Pattern

- Preserve evidence and pause scheduled amplification.
- Separate valid criticism from unsupported claims.
- Correct material inaccuracies without debating individual participants.
- Track brand, support, and revenue signals through the monitoring window.
""",
    "eduky_brand_voice_guide.md": """# Eduky Brand Voice Guide

The fictional brand voice is direct, calm, accountable, and useful.

## Language Principles

- Lead with what is known.
- State uncertainty without speculation.
- Name the action owner and next checkpoint.
- Avoid defensive language and unsupported recovery estimates.
""",
}

CREATOR_OPERATIONS_SKILLS = [
    {
        "skill_id": "SK-prioritization-under-pressure",
        "name": "Prioritization under pressure",
        "description": "Sequence actions by learner impact, reversibility, and business exposure.",
    },
    {
        "skill_id": "SK-customer-communication",
        "name": "Customer communication",
        "description": "Communicate confirmed impact, ownership, uncertainty, and checkpoints.",
    },
    {
        "skill_id": "SK-escalation-judgment",
        "name": "Escalation judgment",
        "description": "Escalate material operational risk to the correct decision owner.",
    },
    {
        "skill_id": "SK-revenue-risk-control",
        "name": "Revenue-risk control",
        "description": "Protect valid transactions and customer trust during recovery.",
    },
    {
        "skill_id": "SK-launch-decision-making",
        "name": "Launch decision-making",
        "description": "Control launch scope, recovery sequencing, and readiness checkpoints.",
    },
    {
        "skill_id": "SK-operational-diagnosis",
        "name": "Operational diagnosis",
        "description": "Use available evidence to isolate failure paths and stabilizing actions.",
    },
    {
        "skill_id": "SK-brand-protection",
        "name": "Brand protection",
        "description": "Respond to public pressure while preserving credibility and trust.",
    },
    {
        "skill_id": "SK-student-success",
        "name": "Student success",
        "description": "Resolve learner-impacting issues with clear ownership and fair policy use.",
    },
    {
        "skill_id": "SK-data-informed-decision",
        "name": "Data-informed decision-making",
        "description": "Use operational and business signals to make bounded decisions.",
    },
    {
        "skill_id": "SK-process-compliance",
        "name": "Process compliance",
        "description": "Apply documented controls and preserve a useful decision record.",
    },
]

CREATOR_OPERATIONS_ROLES = [
    {
        "role_id": "ROLE-FOUNDER-OPERATOR",
        "title": "Founder Operator",
        "description": "Owns cross-functional decisions across learner service, launches, content, and revenue risk.",
        "required_skills": [
            "SK-prioritization-under-pressure",
            "SK-escalation-judgment",
            "SK-revenue-risk-control",
            "SK-data-informed-decision",
        ],
    },
    {
        "role_id": "ROLE-STUDENT-SUCCESS",
        "title": "Student Success Lead",
        "description": "Owns learner support quality, policy execution, and escalation handling.",
        "required_skills": [
            "SK-customer-communication",
            "SK-student-success",
            "SK-escalation-judgment",
        ],
    },
    {
        "role_id": "ROLE-LAUNCH-MANAGER",
        "title": "Launch Manager",
        "description": "Coordinates launch readiness, access, checkout, and recovery decisions.",
        "required_skills": [
            "SK-launch-decision-making",
            "SK-operational-diagnosis",
            "SK-revenue-risk-control",
        ],
    },
    {
        "role_id": "ROLE-CONTENT-OPERATIONS",
        "title": "Content Operations Lead",
        "description": "Coordinates content corrections, public response, and brand safeguards.",
        "required_skills": [
            "SK-brand-protection",
            "SK-customer-communication",
            "SK-data-informed-decision",
        ],
    },
    {
        "role_id": "ROLE-AUTOMATION-OPS",
        "title": "Automation Operations Lead",
        "description": "Maintains controlled workflows, operational evidence, and repeatable procedures.",
        "required_skills": [
            "SK-process-compliance",
            "SK-operational-diagnosis",
            "SK-prioritization-under-pressure",
        ],
    },
]

CREATOR_OPERATIONS_PROFILE = {
    "profile_id": "PROFILE-FOUNDER-OPERATOR-001",
    "display_name": "Founder Operator",
    "role_id": "ROLE-FOUNDER-OPERATOR",
    "context": (
        "Runs a fictional digital education business and makes decisions across "
        "learner support, launches, content operations, and revenue risk."
    ),
    "data_classification": "sanitized-training",
}

CREATOR_OPERATIONS_KNOWLEDGE = {
    "support_policy.md": """# Support Policy

This fictional policy defines consistent support handling for a digital education business.

## Operating Rules

- Acknowledge learner impact before discussing internal ownership.
- Separate urgent access failures from standard guidance requests.
- Escalate repeated access, payment-state, or public-pressure signals.
- Record the decision owner and next checkpoint without personal contact data.
""",
    "refund_handling_guide.md": """# Refund Handling Guide

Use this fictional guide to make fair and consistent training decisions.

## Decision Sequence

1. Confirm the affected product and policy window using sanitized identifiers.
2. Separate access remediation from refund eligibility.
3. Escalate public-pressure cases to the designated operations owner.
4. Communicate the decision, rationale, and next checkpoint without unsupported promises.
""",
    "launch_operations_playbook.md": """# Launch Operations Playbook

Launch operations protect learner access, checkout integrity, and brand trust through staged controls.

## Launch Controls

- Validate checkout, entitlement, and access signals independently.
- Freeze promotional expansion when access integrity is uncertain.
- Use one launch command owner and a fixed checkpoint cadence.
- Restore traffic in stages after successful access verification.
""",
    "student_success_playbook.md": """# Student Success Playbook

Student-success decisions prioritize access restoration, policy clarity, and credible communication.

## Response Pattern

- State the confirmed learner impact.
- Name the current owner and next checkpoint.
- Avoid publishing private learner details.
- Close only after the affected learning path is verified.
""",
    "content_risk_playbook.md": """# Content Risk Playbook

This fictional playbook supports a measured response to public content pressure.

## Response Pattern

- Preserve evidence and pause scheduled amplification.
- Separate valid criticism from unsupported claims.
- Correct material inaccuracies without debating individual participants.
- Track brand, support, and revenue signals through the monitoring window.
""",
    "brand_communications_guide.md": """# Brand Communications Guide

The fictional brand voice is direct, calm, accountable, and useful.

## Language Principles

- Lead with what is known.
- State uncertainty without speculation.
- Name the action owner and next checkpoint.
- Avoid defensive language and unsupported recovery estimates.
""",
}

GENERIC_SKILLS = [
    {
        "skill_id": "SK-prioritization-under-pressure",
        "name": "Prioritization under pressure",
        "description": "Sequence actions by impact, reversibility, and exposure.",
    },
    {
        "skill_id": "SK-customer-communication",
        "name": "Customer communication",
        "description": "Communicate impact, uncertainty, ownership, and checkpoints.",
    },
    {
        "skill_id": "SK-escalation-judgment",
        "name": "Escalation judgment",
        "description": "Escalate material risk to the correct decision owner.",
    },
    {
        "skill_id": "SK-data-informed-decision",
        "name": "Data-informed decision-making",
        "description": "Use bounded evidence to choose and verify actions.",
    },
]


def empty_workspace_template() -> dict[str, Any]:
    return {
        "template_id": "template-empty",
        "name": "Start Empty",
        "description": "Create a blank CRISOL workspace.",
        "workspace": {
            "workspace_id": "WS-LOCAL",
            "workspace_name": "New CRISOL Workspace",
            "organization_name": "",
            "industry": "",
            "data_mode": "empty",
            "load_examples": False,
        },
    }


def eduky_workspace_template() -> dict[str, Any]:
    return {
        "template_id": "template-eduky",
        "name": "Eduky Customer Pack",
        "description": "Optional sanitized first-customer workspace pack.",
        "workspace": {
            "workspace_id": "WS-EDUKY",
            "workspace_name": "Eduky Operations Readiness",
            "organization_name": "Eduky",
            "industry": "Digital Education",
            "data_mode": "workspace",
            "load_examples": False,
        },
        "roles": deepcopy(EDUKY_ROLES),
        "skills": deepcopy(EDUKY_SKILLS),
        "profiles": [deepcopy(EDUKY_PROFILE)],
        "knowledge": deepcopy(EDUKY_KNOWLEDGE),
        "scenarios": [
            support_escalation_scenario_template(),
            launch_day_failure_scenario_template(),
            viral_content_backlash_scenario_template(),
        ],
    }


def creator_operations_workspace_template() -> dict[str, Any]:
    return {
        "template_id": "template-creator-operations",
        "name": "Creator Operations Readiness",
        "description": "Launch, learner support, content, and revenue-risk readiness.",
        "workspace": {
            "workspace_id": "WS-CREATOR-OPERATIONS",
            "workspace_name": "Creator Operations Readiness",
            "organization_name": "",
            "industry": "Digital Education",
            "data_mode": "workspace",
            "load_examples": False,
        },
        "roles": deepcopy(CREATOR_OPERATIONS_ROLES),
        "skills": deepcopy(CREATOR_OPERATIONS_SKILLS),
        "profiles": [deepcopy(CREATOR_OPERATIONS_PROFILE)],
        "knowledge": deepcopy(CREATOR_OPERATIONS_KNOWLEDGE),
        "scenarios": [
            creator_launch_failure_scenario_template(),
            creator_support_escalation_scenario_template(),
            creator_content_backlash_scenario_template(),
        ],
    }


def digital_education_workspace_template() -> dict[str, Any]:
    return _workspace_template(
        template_id="template-digital-education",
        name="Digital Education Operator",
        description="Support, launches, content operations, and student success.",
        workspace_name="Digital Education Operations",
        industry="Digital Education",
        role={
            "role_id": "ROLE-DIGITAL-EDUCATION-OPERATOR",
            "title": "Digital Education Operator",
            "description": "Coordinates learner support, releases, and service continuity.",
            "required_skills": [
                "SK-prioritization-under-pressure",
                "SK-customer-communication",
                "SK-escalation-judgment",
                "SK-data-informed-decision",
            ],
        },
        profile={
            "profile_id": "PROFILE-DIGITAL-EDUCATION-001",
            "display_name": "Digital Education Operator",
            "role_id": "ROLE-DIGITAL-EDUCATION-OPERATOR",
            "context": "Makes sanitized operational decisions across learner support and release readiness.",
        },
        knowledge={
            "digital_education_operations.md": (
                "# Digital Education Operations\n\n"
                "Use one decision owner, protect learner access, and verify recovery before expansion."
            )
        },
        scenarios=[
            _scenario_with_role(
                customer_escalation_template(),
                "ROLE-DIGITAL-EDUCATION-OPERATOR",
                industry="Digital Education",
                scenario_id="SCN-DIGITAL-EDUCATION-SUPPORT-001",
                title="Learner support escalation",
            ),
            _scenario_with_role(
                launch_or_release_failure_template(),
                "ROLE-DIGITAL-EDUCATION-OPERATOR",
                industry="Digital Education",
                scenario_id="SCN-DIGITAL-EDUCATION-RELEASE-001",
                title="Learning product release failure",
            ),
        ],
    )


def customer_support_workspace_template() -> dict[str, Any]:
    return _workspace_template(
        template_id="template-customer-support",
        name="Customer Support Operations",
        description="Escalations, policy handling, retention, and service recovery.",
        workspace_name="Customer Support Operations",
        industry="Customer Service",
        role={
            "role_id": "ROLE-CUSTOMER-SUPPORT-LEAD",
            "title": "Customer Support Lead",
            "description": "Owns escalations, service recovery, and customer communication.",
            "required_skills": [
                "SK-customer-communication",
                "SK-escalation-judgment",
                "SK-prioritization-under-pressure",
            ],
        },
        profile={
            "profile_id": "PROFILE-CUSTOMER-SUPPORT-001",
            "display_name": "Customer Support Lead",
            "role_id": "ROLE-CUSTOMER-SUPPORT-LEAD",
            "context": "Handles sanitized service escalations and retention-risk decisions.",
        },
        knowledge={
            "customer_support_operations.md": (
                "# Customer Support Operations\n\n"
                "Confirm impact, assign one owner, communicate uncertainty, and close with evidence."
            )
        },
        scenarios=[customer_escalation_template()],
    )


def finance_controls_workspace_template() -> dict[str, Any]:
    return _workspace_template(
        template_id="template-finance-controls",
        name="Finance Controls",
        description="Reconciliation, approvals, exceptions, and risk control.",
        workspace_name="Finance Controls Readiness",
        industry="Financial Operations",
        role={
            "role_id": "ROLE-FINANCE-CONTROLS-LEAD",
            "title": "Finance Controls Lead",
            "description": "Owns reconciliation integrity, approvals, and exception control.",
            "required_skills": [
                "SK-data-informed-decision",
                "SK-escalation-judgment",
                "SK-prioritization-under-pressure",
            ],
        },
        profile={
            "profile_id": "PROFILE-FINANCE-CONTROLS-001",
            "display_name": "Finance Controls Lead",
            "role_id": "ROLE-FINANCE-CONTROLS-LEAD",
            "context": "Makes sanitized reconciliation, exception, and approval decisions.",
        },
        knowledge={
            "finance_controls.md": (
                "# Finance Controls\n\n"
                "Preserve the evidence trail, separate exceptions, and require verified approvals."
            )
        },
        scenarios=[finance_reconciliation_control_template()],
    )


def customer_escalation_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-CUSTOMER-ESCALATION-001",
        title="Customer escalation and service recovery",
        industry="Customer Service",
        role_id="ROLE-CUSTOMER-SUPPORT-LEAD",
        minutes=7,
        context="A fictional service issue creates an urgent customer escalation with incomplete evidence.",
        systems=["SVC-orders", "SVC-observability", "SVC-checkout"],
        stakes="Customer trust, retention, and service continuity are at risk.",
        personas=[
            ("Customer Success Lead", "Escalation owner", "empathetic but urgent", "high"),
            ("Service Delivery Lead", "Recovery owner", "direct and evidence-focused", "medium"),
            ("Account Operations Lead", "Commercial impact owner", "calm and outcome-focused", "medium"),
        ],
        knowledge=["customer-support-operations"],
        tags=["customer", "support", "escalation", "retention"],
        turns=_generic_operations_turns("customer escalation", "service evidence"),
    )


def launch_or_release_failure_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-RELEASE-001",
        title="Launch or release failure",
        industry="Digital Services",
        role_id="ROLE-RELEASE-LEAD",
        minutes=8,
        context="A fictional release causes inconsistent access and service behavior.",
        systems=["SVC-checkout", "SVC-identity", "SVC-observability"],
        stakes="Customer access, launch confidence, and near-term revenue are exposed.",
        personas=[
            ("Release Lead", "Release command owner", "direct and urgent", "high"),
            ("Customer Experience Lead", "Customer impact owner", "supportive and urgent", "medium"),
            ("Platform Specialist", "Technical recovery owner", "analytical and precise", "high"),
        ],
        knowledge=["release-control"],
        tags=["launch", "release", "access", "service-recovery"],
        turns=_generic_operations_turns("release failure", "deployment and access evidence"),
    )


def sales_objection_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-SALES-001",
        title="Strategic sales objection",
        industry="Business Services",
        role_id="ROLE-SALES-LEAD",
        minutes=6,
        context="A fictional prospect raises material value, risk, and implementation objections.",
        systems=["SVC-orders", "SVC-observability"],
        stakes="Commercial confidence and a credible next decision are at risk.",
        personas=[
            ("Prospect Operations Lead", "Operational buyer", "analytical and skeptical", "medium"),
            ("Commercial Sponsor", "Business value owner", "calm and outcome-focused", "medium"),
            ("Implementation Lead", "Delivery feasibility owner", "direct and precise", "low"),
        ],
        knowledge=["sales-objection-handling"],
        tags=["sales", "objection", "commercial", "stakeholder"],
        turns=_generic_operations_turns("commercial objection", "value and delivery evidence"),
    )


def data_quality_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-DATA-QUALITY-001",
        title="Data quality incident",
        industry="Analytics",
        role_id="ROLE-DATA-LEAD",
        minutes=8,
        context="A fictional reporting workflow contains delayed and inconsistent data.",
        systems=["SVC-data-pipeline", "SVC-db", "SVC-observability"],
        stakes="Decision confidence and downstream reporting integrity are at risk.",
        personas=[
            ("Data Quality Lead", "Quality gate owner", "analytical and precise", "high"),
            ("Reporting Stakeholder", "Decision consumer", "direct and outcome-focused", "medium"),
            ("Pipeline Specialist", "Recovery owner", "technical and measured", "high"),
        ],
        knowledge=["data-quality-control"],
        tags=["data", "quality", "reporting", "controls"],
        turns=_generic_operations_turns("data quality incident", "quality and lineage evidence"),
    )


def security_response_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-SECURITY-001",
        title="Security response coordination",
        industry="Business Services",
        role_id="ROLE-SECURITY-LEAD",
        minutes=8,
        context="A fictional security signal requires containment, evidence preservation, and communication.",
        systems=["SVC-identity", "SVC-observability", "SVC-orders"],
        stakes="Access integrity, business continuity, and stakeholder confidence are at risk.",
        personas=[
            ("Security Response Lead", "Containment owner", "analytical and urgent", "high"),
            ("Identity Specialist", "Access control owner", "technical and precise", "high"),
            ("Business Continuity Lead", "Operational impact owner", "calm and direct", "medium"),
        ],
        knowledge=["security-response-control"],
        tags=["security", "incident-response", "identity", "risk"],
        turns=_generic_operations_turns("security signal", "access and activity evidence"),
    )


def support_escalation_scenario_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-EDUKY-SUPPORT-001",
        title="Student refund escalation under public pressure",
        industry="Digital Education",
        role_id="ROLE-FOUNDER-OPERATOR",
        minutes=8,
        context=(
            "A fictional learner refund request becomes publicly visible while support "
            "and operations hold incomplete information."
        ),
        systems=["SVC-orders", "SVC-payments", "SVC-observability"],
        stakes=(
            "A fair resolution, support credibility, and launch-period revenue confidence "
            "are at risk."
        ),
        personas=[
            ("Student Success Lead", "Learner resolution owner", "direct", "high"),
            ("Launch Manager", "Operational coordinator", "focused", "medium"),
            ("Founder Operator", "Final decision owner", "calm", "high"),
        ],
        knowledge=[
            "eduky_support_policy",
            "eduky_refund_handling_guide",
            "eduky_student_success_playbook",
        ],
        tags=["student-success", "refund-policy", "public-pressure", "revenue-risk"],
        turns=[
            _turn(
                1,
                "A public refund complaint is gaining attention while support verifies the policy path.",
                "Acknowledge impact and establish one case owner",
                "Create one accountable path while policy and access evidence are checked.",
                ["SK-customer-communication", "SK-student-success"],
                "Ask multiple teams to respond independently",
                "Allow parallel messages before a decision owner is named.",
                ["SK-prioritization-under-pressure"],
            ),
            _turn(
                2,
                "Access history and policy timing are now available through sanitized records.",
                "Separate access recovery from refund eligibility",
                "Resolve immediate learning access while evaluating policy consistently.",
                ["SK-student-success", "SK-data-informed-decision"],
                "Issue a public refund promise immediately",
                "Commit before the policy and access facts are reconciled.",
                ["SK-revenue-risk-control"],
            ),
            _turn(
                3,
                "The public discussion requests a response before the internal review is complete.",
                "Publish a factual checkpoint without private details",
                "State known impact, ownership, and the next update boundary.",
                ["SK-brand-protection", "SK-customer-communication"],
                "Debate the individual complaint publicly",
                "Shift attention from resolution to a personal dispute.",
                ["SK-brand-protection"],
            ),
            _turn(
                4,
                "The review confirms a bounded remedy and a support-process gap.",
                "Apply the remedy and correct the support workflow",
                "Resolve the case and add a repeatable escalation control.",
                ["SK-automation-thinking", "SK-student-success"],
                "Close the case without a workflow correction",
                "Resolve the immediate request but preserve the operational gap.",
                ["SK-automation-thinking"],
            ),
            _turn(
                5,
                "The learner path is restored and public pressure is declining.",
                "Close with evidence and monitor trust signals",
                "Confirm the remedy and retain a short monitoring checkpoint.",
                ["SK-brand-protection", "SK-revenue-risk-control"],
                "End communication as soon as access returns",
                "Leave policy and trust questions without a final checkpoint.",
                ["SK-customer-communication"],
            ),
        ],
    )


def launch_day_failure_scenario_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-EDUKY-LAUNCH-001",
        title="Launch day checkout and access failure",
        industry="Digital Education",
        role_id="ROLE-FOUNDER-OPERATOR",
        minutes=9,
        context=(
            "A fictional course launch sees successful payments but inconsistent learner "
            "entitlement and access signals."
        ),
        systems=["SVC-checkout", "SVC-orders", "SVC-identity"],
        stakes=(
            "Launch revenue, learner access, support capacity, and brand confidence are "
            "exposed during the highest-volume window."
        ),
        personas=[
            ("Launch Manager", "Launch command owner", "focused", "high"),
            ("Student Success Lead", "Learner impact owner", "direct", "high"),
            ("Automation Specialist", "Workflow diagnosis owner", "technical", "medium"),
        ],
        knowledge=["eduky_launch_playbook", "eduky_student_success_playbook"],
        tags=["launch-operations", "checkout", "access", "revenue-risk"],
        turns=[
            _turn(
                1,
                "Payments are completing, but some fictional learner accounts do not receive access.",
                "Pause campaign expansion and isolate the access path",
                "Control new demand while checkout and entitlement signals are separated.",
                ["SK-prioritization-under-pressure", "SK-operational-diagnosis"],
                "Increase promotional traffic",
                "Add demand before the access path is understood.",
                ["SK-launch-decision-making"],
            ),
            _turn(
                2,
                "Evidence points to delayed order-to-access automation rather than payment loss.",
                "Protect order state and reconcile access events",
                "Keep valid payments intact while entitlement events are replayed safely.",
                ["SK-automation-thinking", "SK-data-informed-decision"],
                "Refund every affected order immediately",
                "Create unnecessary revenue loss before access recovery is attempted.",
                ["SK-revenue-risk-control"],
            ),
            _turn(
                3,
                "Support volume is rising and launch messaging is inconsistent.",
                "Establish one launch command update",
                "Align support, operations, and leadership around one checkpoint cadence.",
                ["SK-customer-communication", "SK-escalation-judgment"],
                "Let each team publish its own estimate",
                "Increase confusion and unsupported commitments.",
                ["SK-customer-communication"],
            ),
            _turn(
                4,
                "The access automation is corrected and a bounded replay is available.",
                "Replay access events in verified batches",
                "Restore access with checkpoints before resuming promotion.",
                ["SK-automation-thinking", "SK-launch-decision-making"],
                "Replay all events without checkpoints",
                "Increase duplicate processing and access inconsistency risk.",
                ["SK-operational-diagnosis"],
            ),
            _turn(
                5,
                "Access success is stable and support volume is declining.",
                "Resume launch traffic gradually",
                "Restore demand in stages while monitoring checkout and access together.",
                ["SK-revenue-risk-control", "SK-data-informed-decision"],
                "Return immediately to peak traffic",
                "Remove launch controls before the monitoring window completes.",
                ["SK-launch-decision-making"],
            ),
        ],
    )


def viral_content_backlash_scenario_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-EDUKY-CONTENT-001",
        title="Viral content backlash response",
        industry="Digital Education",
        role_id="ROLE-FOUNDER-OPERATOR",
        minutes=8,
        context=(
            "A fictional educational post is rapidly shared with criticism that mixes a "
            "valid content concern with unsupported claims."
        ),
        systems=["SVC-observability", "SVC-orders", "SVC-checkout"],
        stakes=(
            "Brand trust, learner support volume, scheduled promotion, and near-term "
            "revenue confidence are at risk."
        ),
        personas=[
            ("Content Strategist", "Content correction owner", "measured", "high"),
            ("Student Success Lead", "Learner sentiment owner", "direct", "medium"),
            ("Founder Operator", "Public response owner", "calm", "high"),
        ],
        knowledge=["eduky_content_risk_playbook", "eduky_brand_voice_guide"],
        tags=["content-risk", "brand-protection", "public-response", "revenue-risk"],
        turns=[
            _turn(
                1,
                "The post is spreading quickly and scheduled promotion would amplify it further.",
                "Pause amplification and preserve the content record",
                "Stop additional reach while evidence and context are reviewed.",
                ["SK-brand-protection", "SK-prioritization-under-pressure"],
                "Increase promotion to defend the message",
                "Amplify the disputed content before review.",
                ["SK-brand-protection"],
            ),
            _turn(
                2,
                "Review confirms one material wording problem and several unsupported claims.",
                "Separate the valid issue from unsupported claims",
                "Prepare a precise correction without broadening the dispute.",
                ["SK-data-informed-decision", "SK-brand-protection"],
                "Reject all criticism as inaccurate",
                "Ignore the valid content issue and increase trust risk.",
                ["SK-data-informed-decision"],
            ),
            _turn(
                3,
                "Support needs guidance while the correction is prepared.",
                "Issue an accountable holding statement",
                "Acknowledge review, state the owner, and set a clear next checkpoint.",
                ["SK-customer-communication", "SK-escalation-judgment"],
                "Give support an unverified explanation",
                "Spread inconsistent claims before the correction is approved.",
                ["SK-customer-communication"],
            ),
            _turn(
                4,
                "The corrected content and response are ready.",
                "Publish the correction and explain the change",
                "Address the material issue directly and avoid personal debate.",
                ["SK-brand-protection", "SK-customer-communication"],
                "Remove the post without explanation",
                "Create uncertainty about the content and response standard.",
                ["SK-brand-protection"],
            ),
            _turn(
                5,
                "Sentiment is stabilizing but support and checkout signals require monitoring.",
                "Monitor trust and revenue signals before resuming promotion",
                "Use a bounded observation window before restoring amplification.",
                ["SK-revenue-risk-control", "SK-data-informed-decision"],
                "Resume promotion immediately",
                "Restore reach before confidence signals stabilize.",
                ["SK-prioritization-under-pressure"],
            ),
        ],
    )


def creator_launch_failure_scenario_template() -> dict[str, Any]:
    return _creator_scenario_from(
        launch_day_failure_scenario_template(),
        scenario_id="SCN-CREATOR-LAUNCH-001",
        knowledge_refs=["launch_operations_playbook", "student_success_playbook"],
        personas=[
            ("Launch Coordinator", "Launch command owner", "focused and direct", "high"),
            ("Student Success Lead", "Learner impact owner", "empathetic and urgent", "high"),
            ("Payment Operations Analyst", "Transaction evidence owner", "analytical and precise", "high"),
            ("Brand Communications Lead", "Stakeholder communication owner", "calm and accountable", "medium"),
        ],
    )


def creator_support_escalation_scenario_template() -> dict[str, Any]:
    return _creator_scenario_from(
        support_escalation_scenario_template(),
        scenario_id="SCN-CREATOR-SUPPORT-001",
        knowledge_refs=["support_policy", "refund_handling_guide", "student_success_playbook"],
        personas=[
            ("Student Success Lead", "Learner resolution owner", "empathetic and direct", "high"),
            ("Refund Policy Owner", "Policy decision owner", "measured and precise", "medium"),
            ("Community Manager", "Public channel owner", "calm and responsive", "high"),
            ("Operations Lead", "Cross-functional escalation owner", "direct and accountable", "high"),
        ],
    )


def creator_content_backlash_scenario_template() -> dict[str, Any]:
    return _creator_scenario_from(
        viral_content_backlash_scenario_template(),
        scenario_id="SCN-CREATOR-CONTENT-001",
        knowledge_refs=["content_risk_playbook", "brand_communications_guide"],
        personas=[
            ("Brand Communications Lead", "Public response owner", "calm and accountable", "high"),
            ("Content Strategist", "Content correction owner", "measured and evidence-focused", "high"),
            ("Community Manager", "Audience signal owner", "empathetic and direct", "medium"),
            ("Revenue Owner", "Commercial exposure owner", "analytical and outcome-focused", "medium"),
        ],
    )


def finance_reconciliation_control_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-FINANCE-001",
        title="Finance reconciliation control",
        industry="Digital Services",
        role_id="ROLE-FINANCE-CONTROLS-LEAD",
        minutes=7,
        context="A fictional settlement summary does not match the order ledger.",
        systems=["SVC-payments", "SVC-ledger", "SVC-db"],
        stakes="Revenue reporting and controlled reconciliation are at risk.",
        personas=[
            ("Finance Operations Lead", "Reconciliation owner", "precise", "high"),
            ("Business Operations Lead", "Business decision owner", "calm", "medium"),
        ],
        knowledge=["finance-reconciliation-control"],
        tags=["finance", "reconciliation", "revenue-risk"],
        turns=_generic_operations_turns("reconciliation", "ledger evidence"),
    )


def operations_incident_template() -> dict[str, Any]:
    return _scenario(
        scenario_id="SCN-TEMPLATE-OPS-001",
        title="Operations incident control",
        industry="Digital Services",
        role_id="ROLE-OPERATIONS-LEAD",
        minutes=7,
        context="A fictional business workflow is failing across several operational steps.",
        systems=["SVC-orders", "SVC-observability", "SVC-db"],
        stakes="Customer continuity and operational confidence are at risk.",
        personas=[
            ("Operations Lead", "Incident owner", "direct", "high"),
            ("Service Continuity Lead", "Decision owner", "calm", "medium"),
        ],
        knowledge=["operations-incident-control"],
        tags=["operations", "incident-control", "business-continuity"],
        turns=_generic_operations_turns("operations incident", "workflow evidence"),
    )


def template_catalog() -> dict[str, Any]:
    return {
        "workspace_templates": workspace_template_catalog(),
        "scenario_templates": scenario_template_catalog(),
    }


def workspace_template_catalog() -> list[dict[str, str]]:
    return [
        _template_summary(empty_workspace_template()),
        _template_summary(creator_operations_workspace_template()),
        _template_summary(digital_education_workspace_template()),
        _template_summary(customer_support_workspace_template()),
        _template_summary(finance_controls_workspace_template()),
        _template_summary(eduky_workspace_template()),
    ]


def scenario_template_catalog() -> list[dict[str, Any]]:
    return [
        customer_escalation_template(),
        launch_or_release_failure_template(),
        finance_reconciliation_control_template(),
        operations_incident_template(),
        sales_objection_template(),
        data_quality_template(),
        security_response_template(),
    ]


def workspace_template_by_id(template_id: str) -> dict[str, Any]:
    normalized = template_id.strip().lower()
    aliases = {
        "tpl-empty": "template-empty",
        "tpl-eduky": "template-eduky",
        "eduky": "template-eduky",
        "creator-operations": "template-creator-operations",
        "tpl-creator-operations": "template-creator-operations",
    }
    normalized = aliases.get(normalized, normalized)
    templates = {
        "template-empty": empty_workspace_template,
        "template-creator-operations": creator_operations_workspace_template,
        "template-digital-education": digital_education_workspace_template,
        "template-customer-support": customer_support_workspace_template,
        "template-finance-controls": finance_controls_workspace_template,
        "template-eduky": eduky_workspace_template,
    }
    try:
        return templates[normalized]()
    except KeyError as error:
        raise ValueError(f"Unknown workspace template: {template_id}") from error


def _scenario(
    *,
    scenario_id: str,
    title: str,
    industry: str,
    role_id: str,
    minutes: int,
    context: str,
    systems: list[str],
    stakes: str,
    personas: list[tuple[str, str, str, str]],
    knowledge: list[str],
    tags: list[str],
    turns: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "title": title,
        "industry": industry,
        "role_id": role_id,
        "difficulty": "standard",
        "estimated_minutes": minutes,
        "data_classification": "sanitized-training",
        "business_context": context,
        "systems": systems,
        "initial_stakes": stakes,
        "personas": [
            _persona(persona, role, style, pressure, index)
            for index, (persona, role, style, pressure) in enumerate(personas, start=1)
        ],
        "turns": turns,
        "success_criteria": [
            "Establish accountable ownership",
            "Use evidence before irreversible action",
            "Control customer and revenue exposure",
            "Close with a verified monitoring checkpoint",
        ],
        "failure_modes": [
            "Fragment ownership",
            "Act before evidence is sufficient",
            "Make unsupported public commitments",
        ],
        "knowledge_refs": knowledge,
        "tags": tags,
    }


def _turn(
    number: int,
    situation: str,
    safe_label: str,
    safe_outcome: str,
    safe_skills: list[str],
    risk_label: str,
    risk_outcome: str,
    risk_skills: list[str],
) -> dict[str, Any]:
    return {
        "turn_id": f"T{number}",
        "situation": situation,
        "options": [
            {
                "id": f"OPT-{number}A",
                "label": safe_label,
                "description": safe_outcome,
                "action_type": f"workspace_control_{number}",
                "competencies": safe_skills,
                "risk_effect": "decrease",
                "expected_outcome": safe_outcome,
            },
            {
                "id": f"OPT-{number}B",
                "label": risk_label,
                "description": risk_outcome,
                "action_type": f"workspace_risk_{number}",
                "competencies": risk_skills,
                "risk_effect": "increase",
                "expected_outcome": risk_outcome,
            },
        ],
        "evaluation_focus": sorted(set([*safe_skills, *risk_skills])),
    }


def _generic_operations_turns(topic: str, evidence: str) -> list[dict[str, Any]]:
    situations = [
        f"The {topic} is detected with incomplete impact information.",
        f"The team has enough {evidence} to isolate the highest-risk path.",
        "Stakeholders need one decision owner and a credible checkpoint.",
        "A bounded correction is ready for controlled execution.",
        "The workflow is stable enough for monitored restoration.",
    ]
    safe = [
        ("Establish impact and decision ownership", "Create one controlled response path."),
        ("Validate the highest-risk dependency", "Use evidence to narrow the response."),
        ("Publish a bounded stakeholder checkpoint", "State impact, action, owner, and next review."),
        ("Apply the correction with checkpoints", "Verify each change before expanding scope."),
        ("Restore gradually and monitor", "Close only after business signals stabilize."),
    ]
    risky = [
        ("Act before impact is confirmed", "Increase operational uncertainty."),
        ("Change every dependency at once", "Expand the fault domain."),
        ("Promise a fixed recovery time", "Create an unsupported commitment."),
        ("Skip verification checkpoints", "Reduce evidence quality during recovery."),
        ("Close immediately", "End monitoring before confidence returns."),
    ]
    return [
        _turn(
            index,
            situation,
            safe[index - 1][0],
            safe[index - 1][1],
            ["SK-prioritization-under-pressure", "SK-data-informed-decision"],
            risky[index - 1][0],
            risky[index - 1][1],
            ["SK-escalation-judgment"],
        )
        for index, situation in enumerate(situations, start=1)
    ]


def _workspace_template(
    *,
    template_id: str,
    name: str,
    description: str,
    workspace_name: str,
    industry: str,
    role: dict[str, Any],
    profile: dict[str, Any],
    knowledge: dict[str, str],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "template_id": template_id,
        "name": name,
        "description": description,
        "workspace": {
            "workspace_id": f"WS-{template_id.removeprefix('template-').upper()}",
            "workspace_name": workspace_name,
            "organization_name": "",
            "industry": industry,
            "data_mode": "workspace",
            "load_examples": False,
        },
        "roles": [deepcopy(role)],
        "skills": deepcopy(GENERIC_SKILLS),
        "profiles": [{**deepcopy(profile), "data_classification": "sanitized-training"}],
        "knowledge": deepcopy(knowledge),
        "scenarios": deepcopy(scenarios),
    }


def _scenario_with_role(
    scenario: dict[str, Any],
    role_id: str,
    *,
    industry: str,
    scenario_id: str,
    title: str,
) -> dict[str, Any]:
    return {
        **deepcopy(scenario),
        "scenario_id": scenario_id,
        "title": title,
        "industry": industry,
        "role_id": role_id,
    }


def _creator_scenario_from(
    scenario: dict[str, Any],
    *,
    scenario_id: str,
    knowledge_refs: list[str],
    personas: list[tuple[str, str, str, str]],
) -> dict[str, Any]:
    normalized = deepcopy(scenario)
    normalized["scenario_id"] = scenario_id
    normalized["role_id"] = "ROLE-FOUNDER-OPERATOR"
    normalized["knowledge_refs"] = knowledge_refs
    normalized["personas"] = [
        _persona(persona, role, style, pressure, index)
        for index, (persona, role, style, pressure) in enumerate(personas, start=1)
    ]
    for turn in normalized["turns"]:
        for option in turn["options"]:
            option["competencies"] = [
                "SK-process-compliance"
                if skill == "SK-automation-thinking"
                else skill
                for skill in option["competencies"]
            ]
        turn["evaluation_focus"] = sorted(
            {
                competency
                for option in turn["options"]
                for competency in option["competencies"]
            }
        )
    return normalized


def _template_summary(template: dict[str, Any]) -> dict[str, str]:
    return {
        "template_id": template["template_id"],
        "name": template["name"],
        "description": template["description"],
    }


def _persona(
    persona: str,
    role: str,
    communication_style: str,
    pressure_profile: str,
    index: int,
) -> dict[str, str]:
    style = communication_style.lower()
    if "support" in style or "empathetic" in style:
        voice_style = "supportive"
    elif "technical" in style or "analytical" in style or "precise" in style:
        voice_style = "analytical"
    elif "urgent" in style or pressure_profile == "high":
        voice_style = "urgent"
    else:
        voice_style = "calm"
    avatar_styles = (
        "holographic-operator",
        "holographic-stakeholder",
        "holographic-specialist",
        "holographic-observer",
    )
    return {
        "persona": persona,
        "role": role,
        "communication_style": communication_style,
        "pressure_profile": pressure_profile,
        "voice_style": voice_style,
        "avatar_style": avatar_styles[(index - 1) % len(avatar_styles)],
    }
