from app.validate_release import run_release_validation


def main() -> None:
    report = run_release_validation()
    label = "PASS" if report["release_candidate"] else "FAIL"
    print(f"{label} repository validation")
    print(f"score: {report['score']}")
    print(f"blocking_issues: {len(report['blocking_issues'])}")
    print(f"warnings: {len(report['warnings'])}")
    if not report["release_candidate"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
