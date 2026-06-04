from pathlib import Path

from app.grounding.local_knowledge import DEFAULT_KNOWLEDGE_DIR, load_knowledge_docs


EXPECTED_FILES = [
    "runbook_checkout_outage.md",
    "runbook_database_recovery.md",
    "runbook_incident_escalation.md",
    "postmortem_split_brain.md",
    "cert_az_204_guide.md",
    "cert_az_400_guide.md",
    "cert_dp_203_guide.md",
    "manager_readiness_rubric.md",
]


def main() -> None:
    knowledge_dir = DEFAULT_KNOWLEDGE_DIR
    missing = [file_name for file_name in EXPECTED_FILES if not (knowledge_dir / file_name).exists()]

    if missing:
        raise SystemExit(f"Missing knowledge documents: {', '.join(missing)}")

    documents = load_knowledge_docs(knowledge_dir)
    print(f"knowledge documents: {len(documents)}")

    for file_name in EXPECTED_FILES:
        file_path = knowledge_dir / file_name
        text = Path(file_path).read_text(encoding="utf-8")
        has_disclaimer = "Synthetic demonstration document" in text
        print(f"{file_name}: synthetic_disclaimer={str(has_disclaimer).lower()}")

    print("local packaging summary: ready for local citation fallback")
    print("Azure Foundry IQ indexing is manual/config-driven for now; no upload was performed.")


if __name__ == "__main__":
    main()
