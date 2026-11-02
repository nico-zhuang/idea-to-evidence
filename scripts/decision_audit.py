#!/usr/bin/env python3
"""Structural audit of a decision draft; never verifies the truth of cited facts.

Usage: python3 decision_audit.py [report.json]  # stdin when path omitted
Exit 0 on no structural gaps, 2 on gaps, 1 on malformed input.
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _url(value):
    if not _text(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def audit(report):
    """Return structural issues; an empty list does not prove factual accuracy."""
    if not isinstance(report, dict):
        return ["root: expected JSON object"]
    issues = []
    if report.get("mode") != "research":
        return ["mode: audit applies to research decisions only"]

    intent = report.get("intent")
    if not isinstance(intent, list) or not intent:
        issues.append("intent: record user-stated outcome and any material hypothesis")
        intent = []
    routes = []
    for i, entry in enumerate(intent):
        if not isinstance(entry, dict) or not _text(entry.get("text")):
            issues.append("intent[%d].text: missing" % i)
            continue
        if entry.get("source") not in {"user", "observed", "inference", "unknown"}:
            issues.append("intent[%d].source: label user/observed/inference/unknown" % i)
        if not _text(entry.get("route_change")):
            issues.append("intent[%d].route_change: show decision consequence" % i)
        else:
            routes.append(entry["route_change"].strip().lower())
    if len(routes) > 1 and len(routes) != len(set(routes)):
        issues.append("intent.route_change: two interpretations cannot have identical routes")

    search = report.get("github_search")
    if not isinstance(search, list):
        search = []
    classes = set()
    for i, row in enumerate(search):
        if not isinstance(row, dict) or row.get("class") not in {"solution", "job", "synonym"} or not _text(row.get("query")):
            issues.append("github_search[%d]: class and query required" % i)
        else:
            classes.add(row["class"])
    status = report.get("search_status")
    if status not in {"completed", "blocked", "deferred"}:
        issues.append("search_status: completed, blocked or deferred required")
    if status == "blocked" and not _text(report.get("search_failure")):
        issues.append("search_failure: record attempted query and failure when GitHub is blocked")
    if status == "deferred" and not _text(report.get("search_deferred_reason")):
        issues.append("search_deferred_reason: native-only trial or other safe reason required")
    if status == "completed" and classes != {"solution", "job", "synonym"}:
        issues.append("GitHub search: need solution, job and synonym queries")

    baseline = report.get("baseline")
    if not isinstance(baseline, dict) or not all(_text(baseline.get(key)) for key in ("name", "kind", "fit")):
        issues.append("baseline: current workflow/native/manual/no-action alternative and outcome fit required")
        baseline = {}
    candidates = report.get("candidates", [])
    if not isinstance(candidates, list):
        issues.append("candidates: expected list")
        candidates = []
    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            issues.append("candidates[%d]: expected object" % i)
            continue
        kind = candidate.get("kind")
        if kind not in {"github", "native", "commercial", "manual"} or not _text(candidate.get("name")) or not _text(candidate.get("fit")):
            issues.append("candidates[%d]: kind, name and outcome fit required" % i)
        if kind != "manual" and not _url(candidate.get("url")):
            issues.append("candidates[%d].url: source URL required" % i)
        if kind == "github":
            status_value = candidate.get("license_status")
            if status_value not in {"verified", "absent", "unknown"}:
                issues.append("candidates[%d].license_status: verified/absent/unknown required" % i)
            elif status_value == "verified" and not _url(candidate.get("license_evidence")):
                issues.append("candidates[%d].license_evidence: actual file or detection URL required" % i)

    claims = report.get("claims")
    if not isinstance(claims, list) or not claims:
        issues.append("claims: at least one scoped source-backed claim required")
        claims = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict) or not _text(claim.get("text")):
            issues.append("claims[%d].text: missing" % i)
            continue
        if claim.get("tier") not in {"tested", "official", "third_party", "assumption", "unverified"}:
            issues.append("claims[%d].tier: invalid" % i)
        if not _text(claim.get("scope")):
            issues.append("claims[%d].scope: bound the conclusion" % i)
        if claim.get("tier") in {"official", "third_party"} and not _url(claim.get("source")):
            issues.append("claims[%d].source: opened source URL, not search snippet" % i)
        if claim.get("tier") == "tested":
            if not all(_text(claim.get(key)) for key in ("procedure", "environment", "result")):
                issues.append("claims[%d].procedure/environment/result: required for tested claims" % i)

    crux = report.get("crux")
    if not isinstance(crux, list) or not crux:
        issues.append("crux: at least one decision-changing hypothesis required")
        crux = []
    for i, item in enumerate(crux):
        if not isinstance(item, dict) or item.get("status") not in {"verified", "unverified", "blocked"}:
            issues.append("crux[%d].status: verified/unverified/blocked required" % i)
            continue
        for key in ("text", "test", "pass", "fail"):
            if not _text(item.get(key)):
                issues.append("crux[%d].%s: required" % (i, key))

    decision = report.get("recommendation")
    if not isinstance(decision, dict):
        decision = {}
        issues.append("recommendation: route, condition and next_step required")
    route = decision.get("route")
    if route not in {"reuse", "conditional_reuse", "self_build", "postpone", "reject"}:
        issues.append("recommendation.route: invalid; no blanket ready verdict")
    for key in ("condition", "next_step"):
        if not _text(decision.get(key)):
            issues.append("recommendation.%s: required" % key)
    if route in {"reuse", "conditional_reuse"}:
        target = decision.get("target")
        options = [baseline] + candidates
        match = next((x for x in options if isinstance(x, dict) and x.get("name") == target), None)
        if not _text(target) or match is None:
            issues.append("recommendation.target: name a real baseline or candidate")
        elif match.get("kind") == "github":
            if status != "completed" or len(classes) != 3:
                issues.append("recommendation.target: GitHub candidate reuse requires completed search and source checks")
            if match.get("license_status") != "verified":
                issues.append("recommendation.target: github code reuse needs verified license; absent/unknown is not permission")
    if route == "self_build" and (status != "completed" or len(classes) != 3):
        issues.append("GitHub search incomplete: cannot finalize self-build route")
    return issues


def main():
    try:
        payload = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else sys.stdin.read()
        report = json.loads(payload)
    except (OSError, ValueError) as exc:
        print("Input error: %s" % exc, file=sys.stderr)
        return 1
    issues = audit(report)
    if issues:
        for issue in issues:
            print("- " + issue)
        return 2
    print("Structural checks passed; cited facts and intent still require human/source verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
