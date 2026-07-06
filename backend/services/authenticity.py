import difflib
import json
import re
from typing import Any


HIGH_RISK_FIELDS = {
    "name",
    "email",
    "phone",
    "linkedin",
    "github",
    "education",
    "company",
    "role",
    "duration",
}

HIGH_RISK_PATTERNS = {
    "certification": re.compile(r"\b(certified|certification|certificate|aws|azure|gcp|pmp|cissp)\b", re.I),
    "degree": re.compile(r"\b(bachelor|master|phd|doctorate|degree|university|college|b\.?tech|m\.?tech|b\.?s\.?|m\.?s\.?)\b", re.I),
    "employment_date": re.compile(r"\b(19|20)\d{2}\b|\bjan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec\b", re.I),
}


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _tokenize(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", value.lower())
        if len(token) > 2
    }


def _parse_resume_json(tailored_resume_text: str | None) -> dict[str, Any]:
    if not tailored_resume_text:
        return {}
    try:
        parsed = json.loads(tailored_resume_text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _flatten_resume_lines(value: Any) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []

    def visit(node: Any, path: str):
        if isinstance(node, str):
            text = node.strip()
            if text:
                lines.append((path, text))
            return
        if isinstance(node, list):
            for index, item in enumerate(node):
                visit(item, f"{path}[{index}]")
            return
        if isinstance(node, dict):
            for key, item in node.items():
                visit(item, f"{path}.{key}" if path else key)

    visit(value, "")
    return lines


def _line_similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()


def _best_source_match(generated_line: str, source_lines: list[str]) -> tuple[str | None, float]:
    if not source_lines:
        return None, 0.0
    best_line = max(source_lines, key=lambda source_line: _line_similarity(generated_line, source_line))
    return best_line, _line_similarity(generated_line, best_line)


def _field_name(path: str) -> str:
    return path.split(".")[-1].split("[")[0]


def _is_supported_by_profile(value: str, user_profile: str) -> bool:
    normalized_value = _normalize(value)
    normalized_profile = _normalize(user_profile)
    if normalized_value and normalized_value in normalized_profile:
        return True

    value_tokens = _tokenize(value)
    if not value_tokens:
        return True

    profile_tokens = _tokenize(user_profile)
    overlap = len(value_tokens & profile_tokens) / len(value_tokens)
    return overlap >= 0.6


def _risk_reasons(path: str, value: str, user_profile: str) -> list[str]:
    reasons: list[str] = []
    field = _field_name(path)

    if field in HIGH_RISK_FIELDS and not _is_supported_by_profile(value, user_profile):
        reasons.append(f"{field} is not clearly present in the base profile")

    for label, pattern in HIGH_RISK_PATTERNS.items():
        if pattern.search(value) and not _is_supported_by_profile(value, user_profile):
            reasons.append(f"{label} claim needs review")

    return reasons


def analyze_resume_authenticity(user_profile: str, tailored_resume_text: str | None) -> dict[str, Any]:
    parsed_resume = _parse_resume_json(tailored_resume_text)
    generated_lines = _flatten_resume_lines(parsed_resume) if parsed_resume else []
    source_lines = [line.strip() for line in user_profile.splitlines() if line.strip()]
    source_text = "\n".join(source_lines)
    source_tokens = _tokenize(source_text)

    change_classifications: list[dict[str, Any]] = []
    diff_entries: list[dict[str, Any]] = []
    authenticity_flags: list[dict[str, Any]] = []

    for path, value in generated_lines:
        best_source, similarity = _best_source_match(value, source_lines)
        value_tokens = _tokenize(value)
        token_overlap = len(value_tokens & source_tokens) / len(value_tokens) if value_tokens else 1.0
        risks = _risk_reasons(path, value, user_profile)

        if best_source and _normalize(value) == _normalize(best_source):
            change_type = "Reordered"
        elif similarity >= 0.75:
            change_type = "Rephrased"
        elif similarity >= 0.45 or token_overlap >= 0.6:
            change_type = "Emphasized"
        elif not risks and token_overlap >= 0.35:
            change_type = "Added From Verified Profile"
        else:
            change_type = "Needs Review"

        change_classifications.append(
            {
                "path": path,
                "change_type": change_type,
                "generated_text": value,
                "source_text": best_source,
                "similarity": round(similarity, 3),
                "token_overlap": round(token_overlap, 3),
                "requires_review": change_type == "Needs Review" or bool(risks),
            }
        )

        if best_source and _normalize(value) != _normalize(best_source):
            diff_entries.append(
                {
                    "path": path,
                    "change_type": change_type,
                    "before": best_source,
                    "after": value,
                }
            )
        elif not best_source:
            diff_entries.append(
                {
                    "path": path,
                    "change_type": change_type,
                    "before": None,
                    "after": value,
                }
            )

        for reason in risks:
            authenticity_flags.append(
                {
                    "path": path,
                    "text": value,
                    "reason": reason,
                    "severity": "high",
                    "requires_review": True,
                }
            )

    return {
        "change_classifications": change_classifications,
        "resume_diff": diff_entries[:80],
        "authenticity_flags": authenticity_flags,
        "requires_review": bool(authenticity_flags)
        or any(item["requires_review"] for item in change_classifications),
    }
