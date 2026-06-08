import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterator


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
IGNORED_DIRECTORIES = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "node_modules",
    ".crisol_sessions",
    ".crisol_audio",
    ".crisol_telemetry",
}
TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".css",
    ".dockerignore",
    ".env",
    ".example",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".text",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_FILE_NAMES = {
    ".dockerignore",
    ".gitignore",
    "Dockerfile",
}
PRODUCT_BANNED_TERMS = (
    "hackathon",
    "challenge",
    "contest",
    "judge",
    "submission",
    "demo-only",
    "agents league",
    "run mcp demo",
    "synthetic data only",
)
SAFE_PLACEHOLDER_MARKERS = (
    "<your-",
    "<secure-",
    "your-key",
    "your_key",
    "placeholder",
    "changeme",
    "example-value",
)
SAFE_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "invalid",
    "localhost",
}
POLICY_CONTEXT_MARKERS = (
    "do not",
    "does not",
    "must not",
    "never ",
    "avoid ",
    "prohibited",
    "detect",
    "scan",
    "check for",
    "without ",
    "fictional",
    "placeholder",
)


SECRET_PATTERNS = (
    (
        "provider_api_key",
        re.compile(r"\b(?:sk-ant-|sk-proj-|sk-)[A-Za-z0-9_-]{16,}\b"),
    ),
    (
        "gemini_api_key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    ),
    (
        "jwt_token",
        re.compile(
            r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"
        ),
    ),
    (
        "connection_string_secret",
        re.compile(
            r"(?i)\b(?:AccountKey|SharedAccessKey|Password)\s*=\s*"
            r"(?P<value>[^;\s\"']{8,})"
        ),
    ),
    (
        "named_secret",
        re.compile(
            r"(?i)\b(?:azure[_-]?(?:speech|search|openai)?[_-]?(?:key|api[_-]?key)"
            r"|api[_-]?key|client[_-]?secret|secret[_-]?key|access[_-]?token)"
            r"\s*[:=]\s*[\"']?(?P<value>[A-Za-z0-9+/=_-]{12,})"
        ),
    ),
)
EMAIL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![A-Za-z0-9.-])"
)
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s.-])?(?:\(\d{3}\)|\d{3})[\s.-]"
    r"\d{3}[\s.-]\d{4}(?!\d)"
)
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
SENSITIVE_PHRASES = (
    ("production" + r"\s+" + "password", "production_password"),
    ("secret" + r"\s+" + "key", "secret_key_phrase"),
    ("real" + r"\s+" + "customer", "real_customer_reference"),
    ("confidential" + r"\s+" + "client", "confidential_client_reference"),
    ("internal" + r"\s+" + "customer" + r"\s+" + "data", "internal_customer_data"),
)
PRIVATE_KEY_MARKER = "-" * 5 + "BEGIN " + "PRIVATE KEY" + "-" * 5
SENSITIVE_RULE_DEFINITION_FILES = {
    "backend/app/scenarios/validators.py",
    "backend/app/security/scan.py",
}


def scan_repository_for_secrets(root: Path) -> dict[str, Any]:
    repository_root = root.resolve()
    findings: list[dict[str, Any]] = []

    env_path = repository_root / ".env"
    if _git_tracks(repository_root, ".env"):
        findings.append(
            _finding(
                "tracked_env_file",
                env_path,
                repository_root,
                None,
                "The local .env file is tracked by Git.",
            )
        )
    if env_path.exists() and not _git_ignores(repository_root, ".env"):
        findings.append(
            _finding(
                "unignored_env_file",
                env_path,
                repository_root,
                None,
                "The local .env file is not protected by Git ignore rules.",
            )
        )

    for path in _iter_text_files(repository_root):
        for line_number, line in _read_lines(path):
            if PRIVATE_KEY_MARKER in line:
                findings.append(
                    _finding(
                        "private_key",
                        path,
                        repository_root,
                        line_number,
                        "Private key material marker detected.",
                    )
                )
            for category, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(line):
                    value = match.groupdict().get("value") or match.group(0)
                    if _is_safe_placeholder(value):
                        continue
                    findings.append(
                        _finding(
                            category,
                            path,
                            repository_root,
                            line_number,
                            "Credential-like value detected.",
                        )
                    )

    return _scan_report("secret", findings)


def scan_repository_for_sensitive_data(root: Path) -> dict[str, Any]:
    repository_root = root.resolve()
    findings: list[dict[str, Any]] = []

    for path in _iter_text_files(repository_root):
        for line_number, line in _read_lines(path):
            lower_line = line.lower()
            for match in EMAIL_PATTERN.finditer(line):
                email = match.group(1)
                domain = email.rsplit("@", 1)[-1].lower()
                if domain in SAFE_EMAIL_DOMAINS:
                    continue
                findings.append(
                    _finding(
                        "email_address",
                        path,
                        repository_root,
                        line_number,
                        "Email-like value detected.",
                    )
                )

            for _ in PHONE_PATTERN.finditer(line):
                findings.append(
                    _finding(
                        "phone_number",
                        path,
                        repository_root,
                        line_number,
                        "Phone-like value detected.",
                    )
                )

            for match in CARD_PATTERN.finditer(line):
                digits = re.sub(r"\D", "", match.group(0))
                if 13 <= len(digits) <= 19 and _passes_luhn(digits):
                    findings.append(
                        _finding(
                            "payment_card",
                            path,
                            repository_root,
                            line_number,
                            "Payment-card-like value detected.",
                        )
                    )

            if PRIVATE_KEY_MARKER.lower() in lower_line:
                findings.append(
                    _finding(
                        "private_key",
                        path,
                        repository_root,
                        line_number,
                        "Private key material marker detected.",
                    )
                )

            relative_path = path.relative_to(repository_root).as_posix()
            if relative_path not in SENSITIVE_RULE_DEFINITION_FILES:
                for phrase_pattern, category in SENSITIVE_PHRASES:
                    if re.search(phrase_pattern, lower_line) and not _is_policy_context(lower_line):
                        findings.append(
                            _finding(
                                category,
                                path,
                                repository_root,
                                line_number,
                                "Sensitive business-data phrase detected.",
                            )
                        )

    return _scan_report("sensitive_data", findings)


def scan_product_language(root: Path) -> dict[str, Any]:
    repository_root = root.resolve()
    frontend_root = repository_root / "frontend" / "src"
    findings: list[dict[str, Any]] = []
    files_scanned = 0

    if frontend_root.exists():
        for path in sorted(
            candidate
            for candidate in frontend_root.rglob("*")
            if candidate.is_file() and candidate.suffix.lower() in {".ts", ".tsx"}
        ):
            files_scanned += 1
            for line_number, line in _read_lines(path):
                lower_line = line.lower()
                for term in PRODUCT_BANNED_TERMS:
                    if term in lower_line:
                        findings.append(
                            _finding(
                                "prohibited_product_language",
                                path,
                                repository_root,
                                line_number,
                                f"Prohibited user-facing term detected: {term}",
                            )
                        )

    report = _scan_report("product_language", findings)
    report["files_scanned"] = files_scanned
    return report


def run_security_scan(root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    secret_report = scan_repository_for_secrets(root)
    sensitive_report = scan_repository_for_sensitive_data(root)
    language_report = scan_product_language(root)
    failed = any(
        report["status"] == "fail"
        for report in (secret_report, sensitive_report, language_report)
    )
    return {
        "status": "fail" if failed else "pass",
        "secret_scan": secret_report,
        "sensitive_data_scan": sensitive_report,
        "product_language_scan": language_report,
    }


def _iter_text_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in IGNORED_DIRECTORIES for part in relative_parts):
            continue
        if path.name == ".env":
            continue
        if path.name not in TEXT_FILE_NAMES and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
        except OSError:
            continue
        yield path


def _read_lines(path: Path) -> Iterator[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        yield line_number, line


def _is_safe_placeholder(value: str) -> bool:
    normalized = value.strip("\"'").lower()
    return (
        not normalized
        or normalized.startswith("<")
        or normalized.endswith(">")
        or any(marker in normalized for marker in SAFE_PLACEHOLDER_MARKERS)
    )


def _is_policy_context(line: str) -> bool:
    return any(marker in line for marker in POLICY_CONTEXT_MARKERS)


def _passes_luhn(value: str) -> bool:
    total = 0
    parity = len(value) % 2
    for index, character in enumerate(value):
        digit = int(character)
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _git_tracks(root: Path, relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative_path],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _git_ignores(root: Path, relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", relative_path],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _finding(
    category: str,
    path: Path,
    root: Path,
    line_number: int | None,
    message: str,
) -> dict[str, Any]:
    return {
        "category": category,
        "file": path.resolve().relative_to(root).as_posix(),
        "line": line_number,
        "message": message,
    }


def _scan_report(scan_type: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    unique_findings = []
    seen = set()
    for finding in findings:
        key = (finding["category"], finding["file"], finding["line"])
        if key in seen:
            continue
        seen.add(key)
        unique_findings.append(finding)
    return {
        "scan_type": scan_type,
        "status": "fail" if unique_findings else "pass",
        "finding_count": len(unique_findings),
        "findings": unique_findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan the CRISOL repository for credentials, sensitive data, and product language."
    )
    parser.add_argument("--json", action="store_true", help="Print the complete JSON report.")
    arguments = parser.parse_args()
    report = run_security_scan()

    if arguments.json:
        print(json.dumps(report, indent=2))
    else:
        label = "PASS" if report["status"] == "pass" else "FAIL"
        print(f"{label} security scan")
        print(f"secret_findings: {report['secret_scan']['finding_count']}")
        print(f"sensitive_findings: {report['sensitive_data_scan']['finding_count']}")
        print(
            "product_language_findings: "
            f"{report['product_language_scan']['finding_count']}"
        )

    if report["status"] == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
