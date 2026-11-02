# 本地决策结构审计（高质量模式辅助工具）

当用户已授权研究、当前环境可运行 Python、且任务需给出重要路线建议时，可把**内部草稿**组织成 JSON，通过 `<skill-dir>/scripts/decision_audit.py` 从标准输入或文件校验结构。只读校验，不联网、不运行候选项目、不需要第三方包；用户说“只讨论/不要执行”时**不要调用**。没有本地运行能力时按同一规则人工自检，不虚称通过。

示例：`python3 <skill-dir>/scripts/decision_audit.py /path/to/draft.json`；也可用标准输入避免留下决策草稿文件。退出 0 表示结构完整，退出 2 列出缺口，退出 1 为输入错误。按缺口修订一次，必要时再校验；不要循环填空或把通过当成真实可行性证明。

最小 JSON 形状（具体内容仅举例，不可当真实资料）：

```json
{
  "mode": "research",
  "intent": [
    {"text": "本人会议行动项不漏", "source": "user", "route_change": "查原生纪要和待办"},
    {"text": "可能要求所有会议内容", "source": "inference", "route_change": "先查覆盖范围和合规权限"}
  ],
  "github_search": [
    {"class": "solution", "query": "meeting bot"},
    {"class": "job", "query": "action item tracking"},
    {"class": "synonym", "query": "会议待办"}
  ],
  "search_status": "completed",
  "baseline": {"name": "现有纪要流程", "kind": "native", "fit": "可先人工核对行动项"},
  "candidates": [
    {"name": "项目名称", "kind": "github", "url": "https://github.com/owner/repo", "license_status": "verified", "license_evidence": "https://github.com/owner/repo/blob/main/LICENSE", "fit": "覆盖提取，缺人工核对"}
  ],
  "claims": [
    {"text": "某事件只含元数据", "tier": "official", "source": "https://example.org/docs", "scope": "仅该事件体"}
  ],
  "crux": [
    {"text": "纪要是否满足目标", "status": "unverified", "test": "授权的非敏感案例", "pass": "行动项无漏项", "fail": "有错误归责"}
  ],
  "recommendation": {"route": "conditional_reuse", "target": "现有纪要流程", "condition": "账户授权和效果验证后", "next_step": "先试原生"}
}
```

`source` 值为 `user/observed/inference/unknown`，不能把“资料里提到了”写成 `user`。证据 `tier` 值为 `tested/official/third_party/assumption/unverified`；`tested` 另须 `procedure/environment/result`。路线 `reuse/conditional_reuse/self_build/postpone/reject`，不设笼统的 `ready`。每份报告需有 `baseline`（当前流程、原生、手工或不做）并写明适配；候选 `kind` 可为 `github/native/commercial/manual`。GitHub 仓库的 `license_status` 必须是 `verified/absent/unknown`：只有 `verified` 才需要真实 LICENSE/检测链接；没许可证或尚未核实就如实写 `absent/unknown`，**不能为了脚本过关编造 LICENSE URL**，也不能把该候选作为代码复用目标。`reuse/conditional_reuse` 的 `target` 必须指向 baseline 或一个已列候选。GitHub 全面不可访问时 `search_status=blocked` 且给 `search_failure` 记录查询与失败；若只建议用户已具备的原生能力做低成本试验，可记 `search_status=deferred` 和 `search_deferred_reason`，后续完整方案仍须查 GitHub。`blocked/deferred` 均不可给确定自建结论；`deferred` 也不可推荐仓库源码复用。

**特别重要：通过只代表字段与自洽约束通过。**它无法判断 URL 有没有实际打开、网页是否真写了那句话、用户是否真说过、候选的许可证真伪、实测是否成功；这些必须由原始工具回执、真实用户话语与实验记录核实。不要为了让脚本通过而编造 URL、环境、许可证或用户意图。项目文件中含敏感数据时，勿把内部决策草稿放入公共仓库或在工具输出泄露。
