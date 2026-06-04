from app.grounding.foundry_iq import grounded_answer


QUERIES = [
    "checkout outage database recovery",
    "split brain incident escalation",
    "AZ-400 monitoring CI/CD",
]


def main() -> None:
    for query in QUERIES:
        result = grounded_answer(query, top_k=3)
        citations = result.get("citations", [])

        print(f"query: {query}")
        print(f"mode: {result['mode']}")
        print(f"answer: {result['answer']}")
        print("citations:")
        for citation in citations:
            print(
                f"  - {citation['doc_id']} | {citation['file_name']} | "
                f"{citation['chunk_id']} | {citation['quote']}"
            )
        print()

        if not citations:
            raise SystemExit(f"Grounding query returned zero citations: {query}")


if __name__ == "__main__":
    main()
