"""Structural contract tests; behavior still requires real agent runs."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConditionalCouncilContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        path = ROOT / "references" / "ask-five-gates.md"
        cls.gates = path.read_text(encoding="utf-8") if path.exists() else ""
        cls.review = (ROOT / "references" / "decision-grade-review.md").read_text(encoding="utf-8")
        cls.intent = (ROOT / "references" / "intent-engine.md").read_text(encoding="utf-8")

    def test_depth_routing_preserves_reuse_gate_and_stopping(self):
        for marker in ("对话", "快速试验", "有界比较", "决策级", "共同停止规则", "GitHub 对照明确标待做", "许可证与核心能力均核实"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)
        self.assertIn("三类查询可合并一次搜索请求", self.skill)
        self.assertIn("不推荐自建、源码改造", self.skill)

    def test_skill_routes_to_real_council_reference(self):
        self.assertIn("references/ask-five-gates.md", self.skill)
        self.assertIn("G1", self.skill)
        self.assertIn("G2", self.skill)
        self.assertIn("GitHub", self.skill)

    def test_chinese_idea_deepening_phrase_is_a_discovery_trigger(self):
        frontmatter = self.skill.split("\n---", 1)[0]
        self.assertIn("name: idea-to-evidence", frontmatter)
        self.assertIn("帮我把这个想法深化一下", frontmatter)

    def test_council_requires_execution_not_just_skill_loading(self):
        for marker in ("ask-five-pro", "boundary-guard.py", "match-experts.py", "人格", "实际执行", "未执行"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.gates)

    def test_gates_consume_objections_and_preserve_pause(self):
        for marker in ("G1", "G2", "flash", "pro", "采纳并改变路线", "采纳待核实", "拒绝并说明理由", "议会待确认", "最多两次", "安全"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.gates)

    def test_g1_order_distinguishes_shared_fact_check_from_route_search(self):
        self.assertIn("先核实各路线共用且可自行查的事实", self.skill)
        self.assertIn("G1 先于分支化 GitHub 检索", self.skill)

    def test_user_selected_or_excluded_experts_force_confirmation(self):
        self.assertIn("指定或排除专家", self.gates)
        self.assertIn("等待用户确认", self.gates)

    def test_no_real_customer_case_solicitation_under_data_ban(self):
        self.assertIn("禁止接触工单", self.intent)
        self.assertIn("不要索取最近一次真实客户案例", self.intent)
        self.assertIn("只能讨论公开流程定义或完全虚构情境", self.intent)

    def test_prior_conclusion_cannot_be_relabelled_as_council_gain(self):
        self.assertIn("冻结会前路线与已知阻断", self.gates)
        self.assertIn("会前已排除的候选不能再算议会改变路线", self.gates)
        self.assertIn("验收细化不等于路线翻转", self.gates)

    def test_exclusion_cannot_create_a_homogeneous_pending_panel(self):
        self.assertIn("先剔除用户明确排除的成员，再检查视角互补", self.gates)
        self.assertIn("同质名单不得作为待确认名单展示", self.gates)

    def test_independent_review_is_not_same_model_roleplay(self):
        self.assertIn("独立子代理", self.review)
        self.assertIn("单模型", self.review)
        self.assertIn("议会", self.review)

    def test_eval_input_never_contains_judges_answers(self):
        payload = json.loads((ROOT / "evals" / "ask-five-gates.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(payload["evals"]), 4)
        self.assertEqual(len({row["id"] for row in payload["evals"]}), len(payload["evals"]))
        for row in payload["evals"]:
            with self.subTest(case=row["id"]):
                self.assertNotIn("expected_gate", row)
                self.assertNotIn("expected_behavior", row)
                self.assertIn("prompt", row)


if __name__ == "__main__":
    unittest.main()
