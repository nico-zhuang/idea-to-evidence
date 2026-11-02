import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from decision_audit import audit


VALID = {
    "mode": "research",
    "intent": [
        {"text": "给老板看每周行动项", "source": "user", "route_change": "查纪要任务"},
        {"text": "或要求全量原声", "source": "inference", "route_change": "查原声权限"},
    ],
    "github_search": [
        {"class": "solution", "query": "meeting bot"},
        {"class": "job", "query": "action item tracker"},
        {"class": "synonym", "query": "会议待办"},
    ],
    "search_status": "completed",
    "baseline": {"name": "existing_native", "kind": "native", "fit": "当前纪要可先人工核对"},
    "candidates": [
        {"name": "candidate", "kind": "github", "url": "https://github.com/example/candidate", "license_status": "verified", "license_evidence": "https://github.com/example/candidate/blob/main/LICENSE", "fit": "覆盖提取，缺审阅"}
    ],
    "claims": [
        {"text": "只返回元数据", "tier": "official", "source": "https://example.org/docs/event", "scope": "该事件体，不代表所有接口"}
    ],
    "crux": [
        {"text": "现有纪要是否够用", "status": "unverified", "test": "非敏感合成会议核对", "pass": "行动项与负责人均准确", "fail": "出现遗漏或误派"}
    ],
    "recommendation": {"route": "conditional_reuse", "target": "existing_native", "condition": "授权、功能验证后", "next_step": "先试原生能力"},
}


class DecisionAuditTests(unittest.TestCase):
    def test_valid_conditional_report(self):
        self.assertEqual(audit(copy.deepcopy(VALID)), [])

    def test_self_build_without_search_is_blocked(self):
        report = copy.deepcopy(VALID)
        report["github_search"] = []
        report["recommendation"]["route"] = "self_build"
        self.assertTrue(any("GitHub" in issue for issue in audit(report)))

    def test_search_snippet_cannot_be_official_evidence(self):
        report = copy.deepcopy(VALID)
        report["claims"][0]["tier"] = "official"
        report["claims"][0]["source"] = "search snippet"
        self.assertTrue(any("source" in issue for issue in audit(report)))

    def test_tested_claim_requires_reproducible_context(self):
        report = copy.deepcopy(VALID)
        report["claims"][0]["tier"] = "tested"
        self.assertTrue(any("procedure" in issue for issue in audit(report)))

    def test_ready_route_is_not_a_supported_verdict(self):
        report = copy.deepcopy(VALID)
        report["recommendation"]["route"] = "ready"
        self.assertTrue(any("recommendation.route" in issue for issue in audit(report)))

    def test_baseline_alternative_required(self):
        report = copy.deepcopy(VALID)
        del report["baseline"]
        self.assertTrue(any("baseline" in issue for issue in audit(report)))

    def test_unlicensed_repo_may_be_compared_without_fake_license_url(self):
        report = copy.deepcopy(VALID)
        report["candidates"][0]["license_status"] = "absent"
        report["candidates"][0]["license_evidence"] = None
        self.assertEqual(audit(report), [])

    def test_unlicensed_repo_cannot_be_code_reuse_target(self):
        report = copy.deepcopy(VALID)
        report["candidates"][0]["license_status"] = "absent"
        report["candidates"][0]["license_evidence"] = None
        report["recommendation"]["target"] = "candidate"
        self.assertTrue(any("recommendation.target" in issue and "license" in issue for issue in audit(report)))

    def test_nonexistent_reuse_target_is_rejected(self):
        report = copy.deepcopy(VALID)
        report["recommendation"]["target"] = "missing"
        self.assertTrue(any("target" in issue for issue in audit(report)))

    def test_undifferentiated_intent_routes_are_rejected(self):
        report = copy.deepcopy(VALID)
        report["intent"][1]["route_change"] = report["intent"][0]["route_change"]
        self.assertTrue(any("route_change" in issue for issue in audit(report)))

    def test_blocked_search_allows_conditional_postponement_with_failure_reason(self):
        report = copy.deepcopy(VALID)
        report["github_search"] = []
        report["search_status"] = "blocked"
        report["search_failure"] = "2026-11-01 github search unavailable; attempted meeting bot"
        report["recommendation"]["route"] = "postpone"
        self.assertEqual(audit(report), [])

    def test_native_trial_can_defer_github_with_explicit_reason(self):
        report = copy.deepcopy(VALID)
        report["github_search"] = []
        report["search_status"] = "deferred"
        report["search_deferred_reason"] = "用户已有原生纪要；本次只建议非真实数据的便宜试用，不提自建"
        self.assertEqual(audit(report), [])

    def test_deferred_search_cannot_recommend_repository_reuse(self):
        report = copy.deepcopy(VALID)
        report["github_search"] = []
        report["search_status"] = "deferred"
        report["search_deferred_reason"] = "先试原生"
        report["recommendation"]["target"] = "candidate"
        self.assertTrue(any("recommendation.target" in issue and "GitHub" in issue for issue in audit(report)))

    def test_blocked_github_cannot_support_self_build(self):
        report = copy.deepcopy(VALID)
        report["search_status"] = "blocked"
        report["recommendation"]["route"] = "self_build"
        self.assertTrue(any("GitHub" in issue for issue in audit(report)))


if __name__ == "__main__":
    unittest.main()
